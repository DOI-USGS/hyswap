"""Cumulative calculation functions."""

import numpy as np
import pandas as pd


def calculate_daily_cumulative_values(df, data_column_name,
                                      date_column_name=None):
    """Calculate daily cumulative values.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to calculate cumulative values.
    data_column_name : str
        Name of column containing data to calculate cumulative values for.
    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` will be used.

    Returns
    -------
    cumulative_values : pandas.DataFrame
        DataFrame containing daily cumulative values for each year in the
        input DataFrame, rows are dates and columns include years, days, and
        cumulative values.

    Examples
    --------
    Calculate daily cumulative values from some synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     "date": pd.date_range("2000-01-01", "2000-12-31"),
        ...     "data": np.arange(366)})
        >>> results = cumulative.calculate_daily_cumulative_values(
        ...     df, "data", date_column_name="date")
        >>> results.head()
                    year  day  cumulative
        date
        2000-01-01  2000    1           0
        2000-01-02  2000    2           1
        2000-01-03  2000    3           3
        2000-01-04  2000    4           6
        2000-01-05  2000    5          10
    """
    # if date column is not index, make is so
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # get unique years in the data
    years = df.index.year.unique()
    # make a dataframe to hold cumulative values for each year
    cdf = pd.DataFrame(index=years, columns=np.arange(1, 367))
    # loop through each year and calculate cumulative values
    for year in years:
        # get data for the year
        year_data = df.loc[df.index.year == year, data_column_name]
        # calculate cumulative values and assign to cdf
        cdf.loc[cdf.index == year, :len(year_data)] = year_data.cumsum().values
    # reformat the dataframe
    cdf = _tidy_cumulative_dataframe(cdf)
    return cdf


def _tidy_cumulative_dataframe(cdf):
    """Tidy a cumulative dataframe.

    Parameters
    ----------
    cdf : pandas.DataFrame
        DataFrame containing cumulative values, rows are years, columns are
        days of year.

    Returns
    -------
    cdf : pandas.DataFrame
        DataFrame containing cumulative values, rows are dates, columns include
        years, days, and cumulative values.
    """
    # convert cdf to dataframe organized with full dates on the index
    cdf2 = cdf.stack().reset_index()
    cdf2.columns = ["year", "day", "cumulative"]
    cdf2["date"] = pd.to_datetime(
        cdf2["year"].astype(str) + "-" + cdf2["day"].astype(str),
        format="%Y-%j")
    cdf2 = cdf2.set_index("date")
    return cdf2
