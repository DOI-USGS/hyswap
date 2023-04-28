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

    Default behavior right-aligns the window used for the rolling average,
    and returns NaN values if any of the values in the window are NaN.
    Properties of the windowing can be changed by passing additional keyword
    arguments which are fed to `pandas.DataFrame.rolling`.

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
        `pandas.DataFrame.rolling`.

    Returns
    -------
    pandas.DataFrame
        The output dataframe with the rolling average values.
    """
    df_out = df[data_column_name].rolling(
        data_type, **kwargs).mean().to_frame()
    return df_out
