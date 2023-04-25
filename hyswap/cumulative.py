"""Cumulative calculation functions."""

import numpy as np
import pandas as pd
from hyswap.utils import filter_data_by_day
from hyswap.percentiles import calculate_historic_percentiles


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
    """
    # get unique years in the data
    if date_column_name is None:
        years = df.index.year.unique()
    else:
        years = df[date_column_name].dt.year.unique()
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
    cdf2["date"] = pd.to_datetime(cdf2["year"].astype(str) + "-" + cdf2["day"].astype(str), format="%Y-%j")
    cdf2 = cdf2.set_index("date")
    return cdf2
