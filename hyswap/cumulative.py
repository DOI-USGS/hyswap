"""Cumulative calculation functions."""

import numpy as np
import pandas as pd
from hyswap.utils import define_year_doy_columns


def calculate_daily_cumulative_values(df, data_column_name,
                                      date_column_name=None,
                                      year_type='calendar'):
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
    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".

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
                    year  doy  cumulative
        date
        2000-01-01  2000    1           0
        2000-01-02  2000    2           1
        2000-01-03  2000    3           3
        2000-01-04  2000    4           6
        2000-01-05  2000    5          10
    """
    # set date index, add day/year columns with function
    df = define_year_doy_columns(df, date_column_name=date_column_name,
                                 year_type=year_type, clip_leap_day=True)
    # get unique years in the data
    years = df['index_year'].unique()
    # make a dataframe to hold cumulative values for each year
    cdf = pd.DataFrame(index=years, columns=np.arange(1, 366))
    # loop through each year and calculate cumulative values
    for year in years:
        # get data for the year
        year_data = df.loc[df['index_year'] == year, data_column_name]
        # year must be complete
        if len(year_data) == 365:
            # calculate cumulative values and assign to cdf
            cdf.loc[cdf.index == year, :len(year_data)] = \
                year_data.cumsum().values
    # reformat the dataframe
    cdf = _tidy_cumulative_dataframe(cdf, year_type)
    return cdf


def _tidy_cumulative_dataframe(cdf, year_type):
    """Tidy a cumulative dataframe.

    Parameters
    ----------
    cdf : pandas.DataFrame
        DataFrame containing cumulative values, rows are years, columns are
        days of year.
    year_type : str
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".

    Returns
    -------
    cdf : pandas.DataFrame
        DataFrame containing cumulative values, rows are dates, columns include
        years, day of year (doy), and cumulative values.
    """
    # convert cdf to dataframe organized with full dates on the index
    cdf2 = cdf.stack().reset_index()
    cdf2.columns = ["index_year", "index_doy", "cumulative"]
    # create date column
    if year_type == "calendar":
        cdf2["date"] = pd.to_datetime(
            cdf2["index_year"].astype(str) + "-" +
            cdf2["index_doy"].astype(str),
            format="%Y-%j")
    elif year_type == "water":
        cdf2["date"] = pd.to_datetime(
            cdf2["index_year"].astype(str) + "-" +
            cdf2["index_doy"].astype(str),
            format="%Y-%j") + pd.DateOffset(days=273)
    elif year_type == "climate":
        cdf2["date"] = pd.to_datetime(
            cdf2["index_year"].astype(str) + "-" +
            cdf2["index_doy"].astype(str),
            format="%Y-%j") + pd.DateOffset(days=90)
    # set date to index
    cdf2 = cdf2.set_index("date")
    return cdf2
