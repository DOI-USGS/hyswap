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
    cpf = cfs * 60 * 60 * 24 * freq
    # convert cubic feet per freq to cubic meters per freq
    cpf = cpf * (0.3048 ** 3)
    # convert drainage area km2 to m2
    drainage_area = drainage_area * 1000 * 1000
    # convert cubic meters per year to mm per freq
    mmf = cpf / drainage_area * 1000
    return mmf


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


def identify_sites_from_weights(geom_id,
                                weights_df,
                                geom_id_col,
                                site_col,
                                prop_in_basin_col='pct_in_basin',
                                prop_in_geom_col='pct_in_huc'):

    """Identify sites for a specified geometry.

    Function to identify sites with non-zero weights for a given
    spatial geometry. This function is a helper function that can
    be used to reduce the number of NWIS queries that are performed
    to construct the list of dataframes for a given geometry.

    Parameters
    ----------
    geom_id : str
        Geometry ids to filter to (e.g. geom_id = '03030006').
        Ids range from 8 to 10 digits and sometime involve a leading 0.

    weights_df : pandas.DataFrame
        Tabular dataFrame containing columns the site numbers,
        geometry ids, and two columns wghts in huc and the drainage area basin.

    geom_id_col : str
        Column in weights_df with geometry ids.

    site_col: str
        Column in weights_df with drainage area site numbers.
        Please make sure ids have the correct number of digits and have
          not lost leading 0s when read in.
        If the site numbers are the weights_df index col, site_col = 'index'.

    prop_in_basin_col: str, optional
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'pct_in_basin'

    prop_in_geom_col: str, optional
        Name of column with values (type:float) representing the proportion
        (0 to 1)of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'pct_in_huc'

    Returns
    -------
    list
        List of site IDs with non-zero weights for the geometry

    Examples
    --------
    Find all drainage area site numbers that intersect with geometry id 0101002

    .. doctest::

        >>> data = [['01014000', '01010002', 0.01, 0.6],
        ... ['01014001', '01010002', 0.2, 0.8],
        ... ['01014002', '01010003', 0.9, 0.05]]
        >>> df = pd.DataFrame(data,
        ... columns = ['site_no', 'geom_id', 'wght_basin', 'wght_huc'])
        >>> sites_lst = runoff.identify_sites_from_weights(weights_df=df,
        ... geom_id='01010002', geom_id_col='geom_id', site_col='site_no',
        ... prop_in_basin_col='wght_basin', prop_in_geom_col='wght_huc')
        >>> print(sites_lst)
        ['01014000', '01014001']

    """

    # Filter df to designated geometry (e.g. huc8)
    filtered_df = weights_df[weights_df[geom_id_col] == geom_id]

    # Check that all sites ids have a character count of at least 8
    assert all(filtered_df[site_col].str.len() >= 8), (
        'site numbers char length must be > or = to 8 char')

    # Check whether sites is the df index or not
    if site_col == 'index':
        site_col = filtered_df.index
    else:
        site_col = filtered_df[site_col]

    # Retrieve all non-0 sites within the designated geometry (e.g. huc8)
    site_list = site_col[(filtered_df[prop_in_basin_col] != 0) | (
        filtered_df[prop_in_geom_col] != 0)].to_list()

    return site_list


def calculate_geometric_runoff(geom_id,
                               df_dict,
                               weights_df,
                               site_col,
                               geom_id_col,
                               geom_in_basin_col='prop_in_basin',
                               basin_in_geom_col='prop_in_huc',
                               percentage=False,
                               data_col='runoff'):
    """Function to calculate the runoff for a specified geometry, using
    tabular weights dataframe.

    Parameters
    ----------
    geom_id : str
        Geometry ID for the geometry of interest.

    df_dict : dict
        Dictionary of dataframes containing runoff data for each site in the
        geometry. Each entry in the dictionary takes on the name of the site.

    weights_df : pandas.DataFrame
        Tabular dataFrame containing columns the site numbers,
        geometry ids, and two weight columns: proportion of basin in geom,
        proportion of geom in basin

    site_col : str
        Column in weights_df with drainage area site numbers.
        Please make sure ids have the correct number of digits and have
        not lost leading 0s when read in.
        If the site numbers are the weights_df index col, site_col = 'index'.

    geom_id_col : str
        Column in weights_df with geometry ids.

    geom_in_basin_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'prop_in_basin'

    basin_in_geom_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'prop_in_huc'

    percentage : boolean, optional
        If the weight values in weights_df are percentages, percentage = True.
        If the values are decimal proportions, percentage = False.
        Default: False

    data_col : str, optional
        Column name containing runoff data in the dataframes in df_dict.
        Default is 'runoff', as it is assumed these dataframes are created
        using the :obj:`streamflow_to_runoff` function.

    Returns
    -------
    pandas.Series
        Series containing the area-weighted runoff values for the geometry.
    """
    # check whether sites is the df index or not
    if site_col == 'index':
        weights_df = weights_df.reset_index()
        site_col = weights_df.columns[0]
        weights_df[site_col] = weights_df[site_col].astype(str)
    # assertion to check that site_col are not of type int
    assert weights_df[site_col].dtypes == 'str' or \
        weights_df[site_col].dtypes == 'object', 'weight_df site_col should be a str or obj'  # noqa: E501
    # check if weights are percentage values
    if percentage is True:
        multiplier = 0.01
    else:
        multiplier = 1
    # filtering with copy
    filtered_weights_df = weights_df[weights_df[geom_id_col] == geom_id].copy()
    # converting proportions to decimals if applicable
    filtered_weights_df[geom_in_basin_col] = (filtered_weights_df[geom_in_basin_col] * multiplier)  # noqa: E501
    filtered_weights_df[basin_in_geom_col] = (filtered_weights_df[basin_in_geom_col] * multiplier)  # noqa: E501
    # check to see if there is overlap between geom and
    # basin(s) that is mutually > 0.9
    geom_basin_overlap = filtered_weights_df[(filtered_weights_df[geom_in_basin_col] > 0.9) &  # noqa: E501
                                             (filtered_weights_df[basin_in_geom_col] > 0.9)].copy()  # noqa: E501
    # if geom_basin_overlap is not empty, then the runoff is simply
    # the runoff from the basin with proportion overlap of > 0.9 AND
    # the highest weight.
    if ~geom_basin_overlap.empty:
        # calculate weight(s) - need weights to determine which
        # basin should be used to represent geom's runoff
        geom_basin_overlap['weight'] = geom_basin_overlap[basin_in_geom_col] * geom_basin_overlap[geom_in_basin_col]  # noqa: E501
        # order by weight in descending order
        geom_basin_overlap = geom_basin_overlap.sort_values(by='weight',
                                                            ascending=False)
        # sites ordered in descending order from highest to lowest weight
        sites = geom_basin_overlap[site_col]
        # check to see which sites are in dictionary
        sites_w_data = [site for site in sites if site in df_dict]
        # if sites exist in dictionary, use the basin with the highest
        # weight, i.e. max(proportion in geom x proportion in basin)
        if bool(sites_w_data):
            # this site's runoff will be the geom's estimated runoff
            geom_runoff = df_dict[sites_w_data[0]].runoff
            geom_runoff = geom_runoff.rename('geom_runoff')
            return geom_runoff
        else:
            print('Weights table contains basins that overlap with geom > 0.9, but no runoff data exists for basins that meet this critera. Continuing to alternative calculation of runoff')  # noqa: E501
    # If return not executed, then go to the next step of
    # finding basins within the geom and the basin that contains
    # the geom with the largest weight
    # find where geom in basin is ~ 1 (contained by basin)
    geom_in_basin = filtered_weights_df[(filtered_weights_df[geom_in_basin_col] > 0.98)].copy()  # noqa: E501
    # find basins with data in runoff dictionary
    geom_in_basin = geom_in_basin[geom_in_basin[site_col].map(df_dict).notna()]  # noqa: E501
    # if there are no basins containing the geometry object
    # with associated runoff data, return an empty series.
    if geom_in_basin.empty:
        geom_runoff = pd.Series(dtype='float32')
        print("No runoff data associated with any basins containing the geometry object for the time period selected. Returning empty series.")  # noqa: E501
        return geom_runoff
    else:
        # calculate their weights
        geom_in_basin['weight'] = geom_in_basin[basin_in_geom_col] * \
            geom_in_basin[geom_in_basin_col]
        # grab basin with greatest weight value: this means it fully
        # contains the geom and closest in size to geom (a larger
        # basin would result in a smaller overall weight since the
        # proportion of the basin in geom would be smaller with a
        # bigger basin)
        geom_in_basin = geom_in_basin[geom_in_basin['weight'] == geom_in_basin['weight'].max()]  # noqa: E501
    # grab all basins fully contained within the geom
    basin_in_geom = filtered_weights_df[(filtered_weights_df[basin_in_geom_col] > 0.98)].copy()  # noqa: E501
    # find basins with data in runoff dictionary
    basin_in_geom = basin_in_geom[basin_in_geom[site_col].map(df_dict).notna()]  # noqa: E501
    # if there are no basins with runoff data, return an empty series.
    if basin_in_geom.empty:
        print("No runoff data associated with any basins contained within the geometry object for the time period selected. Only using the basin containing the geometry to estimate runoff.")  # noqa: E501
    else:
        # calculate their weights
        basin_in_geom['weight'] = basin_in_geom[basin_in_geom_col] * \
            basin_in_geom[geom_in_basin_col]
    # combine these two dfs into one
    final_weights_df = pd.concat([geom_in_basin, basin_in_geom])
    print(final_weights_df)
    # grab applicable basin runoff from dictionary
    basins = final_weights_df[site_col].tolist()
    basins_runoff = pd.concat([df_dict[basin] for basin in basins])
    # put dates in column so func can group by them
    basins_runoff['date'] = basins_runoff.index
    # merge basin weight info to basin runoff data
    weights_runoff = basins_runoff.merge(final_weights_df, left_on='site_no', right_on=site_col)  # noqa: E501
    # get weighted runoff value for each day
    weights_runoff['basin_weighted_runoff'] = weights_runoff[data_col] * weights_runoff['weight']  # noqa: E501
    # apply equation to each day to get estimated huc runoff
    geom_runoff_df = weights_runoff.groupby('date').apply(lambda x: x['basin_weighted_runoff'].sum()/x['weight'].sum()).reset_index(name='geom_runoff')  # noqa: E501
    geom_runoff = geom_runoff_df.set_index('date')['geom_runoff']\
        .rename_axis('datetime')
    return geom_runoff


def calculate_multiple_geometric_runoff(
        geom_id_list,
        df_dict,
        weights_df,
        site_col,
        geom_id_col,
        geom_in_basin_col='prop_in_basin',
        basin_in_geom_col='prop_in_huc',
        percentage=False,
        data_col='runoff'
        ):
    """Calculate runoff for multiple geometries at once.

    Parameters
    ----------
    geom_id_list : list
        List of geometry ID strings for the geometries of interest.
        These should be columns in the weights matrix.

    df_dict : dict
        Dictionary of dataframes containing runoff data for each site in the
        geometry.

    weights_df : pandas.DataFrame
        Tabular dataFrame containing columns the site numbers,
        geometry ids, and two weight columns: proportion of basin
        in huc, proportion of huc in basin.

    site_col : str
        Column in weights_df with drainage area site numbers.
        Please make sure ids have the correct number of digits
        and have not lost leading 0s when read in. If the site
        numbers are the weights_df index col, site_col = 'index'.

    geom_id_col : str
        Column in weights_df with geometry ids.

    geom_in_basin_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'pct_in_basin'

    basin_in_geom_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'pct_in_huc'

    percentage : boolean, optional
        If the weight values in weights_df are percentages, percentage = True.
        If the values are decimal proportions, percentage = False.
        Default: False

    data_col : str, optional
        Column name containing runoff data in the dataframes in df_dict.
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
    # loop through geom_id_list to calculate runoff for each geometry
    for geom_id in geom_id_list:
        runoff_sites = identify_sites_from_weights(
            geom_id=geom_id,
            weights_df=weights_df,
            geom_id_col='huc_id',
            site_col='da_site_no',
            prop_in_basin_col='prop_in_basin',
            prop_in_geom_col='prop_in_huc'
            )
        # subset dictionary to sites with drainage areas that
        # intersect the geom_id
        site_dict = {site_no: df_dict[site_no]
                     for site_no in runoff_sites if site_no in df_dict}
        # calculate runoff for geometry
        runoff = calculate_geometric_runoff(
            geom_id=geom_id,
            df_dict=site_dict,
            weights_df=weights_df,
            site_col=site_col,
            geom_id_col=geom_id_col,
            basin_in_geom_col=basin_in_geom_col,
            geom_in_basin_col=geom_in_basin_col,
            percentage=percentage,
            data_col=data_col)

        # add runoff to results_df
        results_df[geom_id] = runoff.to_frame()
    return results_df
