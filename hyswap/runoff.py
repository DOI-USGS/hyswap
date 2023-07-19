"""Runoff functions for hyswap."""
import pandas as pd


def convert_cfs_to_runoff(cfs, drainage_area, frequency="annual"):
    """Convert cfs to runoff values for some drainage area.

    Parameters
    ----------
    cfs : float
        Flow in cubic feet per second.

    drainage_area : float
        Drainage area in km2.

    frequency : str, optional
        Frequency of runoff values to return. Options are 'annual',
        'monthly', and 'daily'. Default is 'annual'.

    Returns
    -------
    float
        Runoff in mm/<frequency>.

    Examples
    --------
    Convert 14 cfs to mm/yr for a 250 km2 drainage area.

    .. doctest::

        >>> mmyr = runoff.convert_cfs_to_runoff(14, 250)
        >>> np.round(mmyr)
        50.0
    """
    # convert frequency string to value
    if frequency == "annual":
        freq = 365.25
    elif frequency == "monthly":
        freq = 365.25 / 12
    elif frequency == "daily":
        freq = 1
    else:
        raise ValueError("Invalid frequency: {}".format(frequency))
    # convert cfs to cubic feet per frequency
    cpy = cfs * 60 * 60 * 24 * freq
    # convert cubic feet per freq to cubic meters per freq
    cpy = cpy * (0.3048 ** 3)
    # convert drainage area km2 to m2
    drainage_area = drainage_area * 1000 * 1000
    # convert cubic meters per year to mm per freq
    mmyr = cpy / drainage_area * 1000
    return mmyr


def streamflow_to_runoff(df, data_col, drainage_area, frequency="annual"):
    """Convert streamflow to runoff for a given drainage area.

    For a given gage/dataframe, convert streamflow to runoff using the
    drainage area and the convert_cfs_to_runoff function.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing streamflow data.

    data_col : str
        Column name containing streamflow data, assumed to be in cfs.

    drainage_area : float
        Drainage area in km2.

    frequency : str, optional
        Frequency of runoff values to return. Options are 'annual',
        'monthly', and 'daily'. Default is 'annual'.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing runoff data in a column named 'runoff'.

    Examples
    --------
    Convert streamflow to runoff for a given drainage area.

    .. doctest::

        >>> df = pd.DataFrame({'streamflow': [14, 15, 16]})
        >>> runoff_df = runoff.streamflow_to_runoff(df, 'streamflow', 250)
        >>> print(runoff_df['runoff'].round(1))
        0    50.0
        1    53.6
        2    57.2
        Name: runoff, dtype: float64
    """
    df['runoff'] = df[data_col].apply(
        lambda x: convert_cfs_to_runoff(x, drainage_area, frequency=frequency)
    )
    return df


def calculate_geometric_runoff(geoid, df_list, weights_matrix,
                               start_date=None, end_date=None,
                               data_col='runoff'):
    """Function to calculate the runoff for a specified geometry.

    Parameters
    ----------
    geoid : str
        Geometry ID for the geometry of interest.

    df_list : list
        List of dataframes containing runoff data for each site in the
        geometry.

    weights_matrix : pandas.DataFrame
        DataFrame containing the weights for all sites and all geometries.
        Columns are geometry IDs, index is site IDs.

    start_date : str, optional
        Start date for the runoff calculation. If not specified, the earliest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    end_date : str, optional
        End date for the runoff calculation. If not specified, the latest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    data_col : str, optional
        Column name containing runoff data in the dataframes in df_list.
        Default is 'runoff', as it is assumed these dataframes are created
        using the :obj:`streamflow_to_runoff` function.

    Returns
    -------
    pandas.Series
        Series containing the area-weighted runoff values for the geometry.
    """
    # get date range
    date_range = _get_date_range(df_list, start_date, end_date)

    # get site list from weights matrix index
    site_list = weights_matrix.index.tolist()

    # create empty dataframe to store results, index is site_list,
    # columns are date_range
    runoff_df = pd.DataFrame(index=site_list, columns=date_range)

    # loop through the df_list to populate rows of the runoff_df
    for df in df_list:
        # get site id (assumed to be string from NWIS)
        site_id = df['site_no'][0]
        # convert site_id to int for indexing weights matrix
        site_id = int(site_id)
        # get weight for site
        weight = weights_matrix[geoid].loc[site_id]
        # get runoff for site
        runoff = df[data_col]
        # multiply weights by runoff
        weighted_runoff = weight * runoff
        # add weighted runoff to runoff_df
        # pandas seems to use dates to automatically align data :)
        runoff_df.loc[site_id] = weighted_runoff

    # combine the new runoff_df with the existing weights matrix to calculate
    # the area-weighted runoff values for the geometry
    runoff_sum = runoff_df.sum(axis=0, skipna=True)
    weights_sum = weights_matrix[geoid].sum(skipna=True)
    weighted_runoff = runoff_sum / weights_sum

    return weighted_runoff


def _get_date_range(df_list, start_date, end_date):
    """Get date range for runoff calculation.

    This is an internal function used by the :obj:`calculate_geometric_runoff`
    function to get the date range for the runoff calculation. If no start or
    end date is specified, the earliest/latest date in the df_list will be
    used.

    Parameters
    ----------
    df_list : list
        List of dataframes containing runoff data for each site in the
        geometry.

    start_date : str, optional
        Start date for the runoff calculation. If not specified, the earliest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    end_date : str, optional
        End date for the runoff calculation. If not specified, the latest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    Returns
    -------
    pandas.DatetimeIndex
        DatetimeIndex containing the date range for the runoff calculation.
    """
    if start_date is None:
        # if no start date iterate through df_list to find earliest date
        start_date = df_list[0].index[0]
        for df in df_list:
            if df.index[0] < start_date:
                start_date = df.index[0]
    else:
        # make the string tz-aware
        start_date = pd.to_datetime(start_date).tz_localize("UTC")
    if end_date is None:
        # if no end date iterate through df_list to find latest date
        end_date = df_list[0].index[-1]
        for df in df_list:
            if df.index[-1] > end_date:
                end_date = df.index[-1]
    else:
        # make the string tz-aware
        end_date = pd.to_datetime(end_date).tz_localize("UTC")
    # create range of dates from start to end
    date_range = pd.date_range(start_date, end_date)

    return date_range


def identify_sites_for_location(geoid, weights_matrix):
    """Identify sites for a given geometry.

    Function to identify sites with non-zero weights for a given
    spatial geometry. This function is a helper function that can
    be used to reduce the number of NWIS queries that are performed
    to construct the list of dataframes for a given geometry.

    Parameters
    ----------
    geoid : str
        Geometry ID for the geometry of interest; should be a column
        in the weights matrix.

    weights_matrix : pandas.DataFrame
        DataFrame containing the weights for all sites and all geometries.
        Columns are geometry IDs, index is site IDs.

    Returns
    -------
    list
        List of site IDs with non-zero weights for the geometry.
    """
    int_list = weights_matrix.index[weights_matrix[geoid] > 0].tolist()
    site_list = [str(i).zfill(8) for i in int_list]
    return site_list


def calculate_multiple_geometric_runoff(
        geoid_list, df_list, weights_matrix,
        start_date=None, end_date=None, data_col='runoff'):
    """Calculate runoff for multiple geometries at once.

    Parameters
    ----------
    geoid : list
        List of geometry ID strings for the geometries of interest.
        These should be columns in the weights matrix.

    df_list : list
        List of dataframes containing runoff data for each site in the
        geometry.

    weights_matrix : pandas.DataFrame
        DataFrame containing the weights for all sites and all geometries.
        Columns are geometry IDs, index is site IDs.

    start_date : str, optional
        Start date for the runoff calculation. If not specified, the earliest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    end_date : str, optional
        End date for the runoff calculation. If not specified, the latest
        date in the df_list will be used. Format is 'YYYY-MM-DD'.

    data_col : str, optional
        Column name containing runoff data in the dataframes in df_list.
        Default is 'runoff', as it is assumed these dataframes are created
        using the :obj:`streamflow_to_runoff` function.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the area-weighted runoff values for each
        geometry. Columns are geometry IDs, index is date range.
    """
    # create empty dataframe to store results
    results_df = pd.DataFrame()
    # loop through geoid_list to calculate runoff for each geometry
    for geoid in geoid_list:
        # calculate runoff for geometry
        runoff = calculate_geometric_runoff(
            geoid, df_list, weights_matrix,
            start_date=start_date, end_date=end_date,
            data_col=data_col)
        # add runoff to results_df
        results_df[geoid] = runoff.to_frame()
    return results_df
