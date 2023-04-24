"""Utility functions for hyswap."""


def filter_approved_data(data, filter_column=None):
    """Filter a dataframe to only return approved "A" data.

    Parameters
    ----------
    data : pandas.DataFrame
        The data to filter.
    filter_column : string
        The column upon which to filter. If None, an error will be raised.

    Returns
    -------
    pandas.DataFrame
        The filtered data.
    """
    if filter_column is None:
        raise ValueError("filter_column must be specified.")
    return data.loc[data[filter_column] == "A"]


def rolling_average(df, data_column_name, data_type, **kwargs):
    """Calculate a rolling average for a dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to calculate the rolling average for.
    data_column_name : string
        The name of the column to calculate the rolling average for.
    data_type : string
        The formatted frequency string to be used with
        pandas.DataFrame.rolling to calculate the average over the correct
        temporal period.
    **kwargs
        Additional keyword arguments to be passed to
        pandas.DataFrame.rolling.

    Returns
    -------
    pandas.DataFrame
        The output dataframe with the rolling average values.
    """
    df_out = df[data_column_name].rolling(
        data_type, **kwargs).mean().to_frame()
    return df_out


def filter_data_by_day(df, doy, data_column_name, date_column_name=None):
    """Filter data by day of year.
        DataFrame containing data to filter.

    doy : int
        Day of year to filter.

    data_column_name : str
        Name of column containing data to filter.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    Returns
    -------
    data : array_like
        Data from the specified day of year.
    """
    # grab data from the specified day of year
    if date_column_name is None:
        dff = df.loc[df.index.dayofyear == doy, data_column_name]
    else:
        dff = df.loc[df[date_column_name].dt.dayofyear == doy,
                     data_column_name]
    # return data as a 1-D numpy array
    return dff.values
