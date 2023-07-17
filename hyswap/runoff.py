"""Runoff functions for hyswap."""


def convert_cfs_to_mmyr(cfs, drainage_area):
    """Convert cfs to mm/yr.

    Parameters
    ----------
    cfs : float
        Flow in cubic feet per second.

    drainage_area : float
        Drainage area in km2.

    Returns
    -------
    float
        Runoff in mm/yr.

    Examples
    --------
    Convert 14 cfs to mm/yr for a 250 km2 drainage area.

    .. doctest::

        >>> mmyr = runoff.convert_cfs_to_mmyr(14, 250)
        >>> np.round(mmyr)
        50.0
    """
    # convert cfs to cubic feet per year
    cpy = cfs * 60 * 60 * 24 * 365.25
    # convert cubic feet per year to cubic meters per year
    cpy = cpy * (0.3048 ** 3)
    # convert drainage area km2 to m2
    drainage_area = drainage_area * 1000 * 1000
    # convert cubic meters per year to mm per year
    mmyr = cpy / drainage_area * 1000
    return mmyr


def streamflow_to_runoff(df, data_col, drainage_area):
    """Convert streamflow to runoff for a given drainage area.

    For a given gage/dataframe, convert streamflow to runoff using the
    drainage area and the convert_cfs_to_mmyr function.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing streamflow data.

    data_col : str
        Column name containing streamflow data, assumed to be in cfs.

    drainage_area : float
        Drainage area in km2.

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
        lambda x: convert_cfs_to_mmyr(x, drainage_area)
    )
    return df
