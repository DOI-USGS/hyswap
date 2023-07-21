"""Runoff functions for hyswap."""


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


def calculate_area_weighted_runoff(weights, runoff):
    """Calculate area weighted runoff for an area.

    Parameters
    ----------
    weights : pandas.Series
        pandas.Series containing weights for each gage in the specified area.
        Generally a specific column selected from a larger weights DataFrame
        which has areas as the column headers and each row corresponds to a
        gage.

    runoff : pandas.DataFrame
        DataFrame containing runoff values for gage. Expect to have each row
        correspond to a gage,

    Returns
    -------
    float
        Area weighted runoff.
    """
