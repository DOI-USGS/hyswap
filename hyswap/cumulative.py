"""Cumulative calculation functions."""

import pandas as pd
from hyswap.utils import define_year_doy_columns


def calculate_daily_cumulative_values(df, data_column_name,
                                      date_column_name=None,
                                      year_type='calendar',
                                      unit='acre-feet',
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
    unit : str, optional
        The unit the user wants to use to report cumulative flow. One of
        'acre-feet', 'cfs', 'cubic-meters', 'cubic-feet'. Assumes input
        data are in cubic feet per second (cfs).

    Returns
    -------
    cumulative_values : pandas.DataFrame
        DataFrame containing daily cumulative values for each year in the
        input DataFrame, rows are dates and columns include years, month-days,
        day-of-year and cumulative values in the units specified.

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
        ['index_month_day', 'index_year', 'index_doy', 'cumulative']
    """
    # check that unit is valid
    if unit not in ['acre-feet', 'cfs', 'cubic-meters', 'cubic-feet']:
        raise ValueError(
            'Unit must be one of "acre-feet", "cfs", "cubic-meters", "cubic-feet"')  # noqa: E501
    # set date index, add day/year columns with function
    df = define_year_doy_columns(df,
                                 date_column_name=date_column_name,
                                 year_type=year_type,
                                 clip_leap_day=clip_leap_day)
    # get unique years in the data
    years = df['index_year'].unique()

    # make an empty dataframe to hold cumulative values for each year
    cdf = pd.DataFrame([])
    selected_columns = [
        data_column_name,
        'index_month_day',
        'index_year',
        'index_doy'
        ]
    # loop through each year and calculate cumulative values
    for year in years:
        # get data for the year
        year_data = df[df['index_year'] == year][selected_columns]
        year_data = year_data.sort_index()
        # calculate cumulative values and assign to cdf
        if unit == 'acre-feet':
            # convert cubic feet to acre-feet
            # multiplied by seconds per day
            year_data['cumulative'] = year_data[data_column_name].cumsum().values * 0.0000229568 * 86400  # noqa: E501
        elif unit == 'cubic-meters':
            # convert cubic feet to cubic meters
            # multiplied by seconds per day
            year_data['cumulative'] = year_data[data_column_name].cumsum().values * 0.02831685 * 86400  # noqa: E501
        elif unit == 'cubic-feet':
            # convert cubic feet per second to cubic feet
            # multiplied by seconds per day
            year_data['cumulative'] = year_data[data_column_name].cumsum().values * 86400  # noqa: E501
        else:
            year_data['cumulative'] = year_data[data_column_name].cumsum().values  # noqa: E501
        cdf = pd.concat([cdf, year_data])
    cdf = cdf[['index_month_day', 'index_year', 'index_doy', 'cumulative']]
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
