"""Cumulative calculation functions."""

import numpy as np
import pandas as pd
from hyswap.utils import define_year_doy_columns


def calculate_daily_cumulative_values(df, data_column_name,
                                      date_column_name=None,
                                      year_type='calendar',
                                      clip_leap_day=False):
    """Calculate daily cumulative values.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to calculate cumulative values.
    data_column_name : str
        Name of column containing data to calculate cumulative values for.
        Discharge data assumed to be in unit of ft3/s.
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
        cumulative values in acre-feet.

    Examples
    --------
    Calculate daily cumulative values from some synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     "date": pd.date_range("2000-01-01", "2000-12-31"),
        ...     "data": np.arange(366)})
        >>> results = cumulative.calculate_daily_cumulative_values(
        ...     df, "data", date_column_name="date")
        >>> results.columns.tolist()
        ['index_year', 'index_doy', 'cumulative']
    """
    # set date index, add day/year columns with function
    df = define_year_doy_columns(df, date_column_name=date_column_name,
                                 year_type=year_type, clip_leap_day=clip_leap_day)
    # get unique years in the data
    years = df['index_year'].unique()

    # Set up month-day index for cdf dataframe
    if year_type is 'water':
        date_range = pd.date_range(start = "10-01-1999", end = "09-30-2000", freq="D")
    elif year_type is 'climate':
        date_range = pd.date_range(start = "04-01-1999", end = "03-31-2000", freq="D")
    else:
        date_range = pd.date_range(start = "01-01-2000", end = "12-31-2000", freq="D")
    date_range = date_range.strftime("%m-%d")
    
    # make an empty dataframe to hold cumulative values for each year
    cdf = pd.DataFrame(columns=date_range)
    # loop through each year and calculate cumulative values
    for year in years:
        # get data for the year
        year_data = df.loc[df['index_year'] == year,[data_column_name, 'index_month_day', 'index_year']]
        year_data = year_data.sort_index(inplace=True)
        # year must be complete
        if len(year_data) >= 365:
            # calculate cumulative values and assign to cdf
            # converted to acre-feet
            # multiplied by seconds per day
            year_data['cumulative'] = year_data[data_column_name].cumsum().values * 0.0000229568 * 86400
            year_data_pivot = year_data.pivot(index = 'index_year', columns = 'index_month_day', values='cumulative')
        else:
            year_data_pivot = pd.DataFrame([])
        cdf = pd.concat([cdf, year_data_pivot])
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
