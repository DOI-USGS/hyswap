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
