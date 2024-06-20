"""Raster hydrograph functionality."""

import pandas as pd
from hyswap.utils import rolling_average
from hyswap.utils import define_year_doy_columns
from hyswap.utils import set_data_type


def format_data(df, data_column_name, date_column_name=None,
                data_type='daily', year_type='calendar',
                begin_year=None, end_year=None,
                clip_leap_day=False, **kwargs):
    """
    Format data for raster hydrograph.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    data_column_name : str
        The name of the column containing the data.
    date_column_name : str, optional
        The name of the column containing the date. Default is None which
        assumes the index is the date.
    data_type : str, optional
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. Default is 'daily'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.
    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".
    begin_year : int, optional
        The first year to include in the data. Default is None which uses the
        first year in the data.
    end_year : int, optional
        The last year to include in the data. Default is None which uses the
        last year in the data.
    clip_leap_day : bool, optional
        If True, removes leap day '02-29' from the percentiles dataset
        used to create the plot. Defaults to False.
    **kwargs
        Keyword arguments to pass to the pandas.DataFrame.rolling method.

    Returns
    -------
    pandas.DataFrame
        The formatted data starting on the first day of the first year and
        ending on the last day of the last year with the specified data type
        and year type.

    Examples
    --------
    Formatting synthetic daily data for a raster hydrograph.

    .. doctest::
        :skipif: True  # docstrings test fails with np.float64

        >>> df = pd.DataFrame({'date': pd.date_range('1/1/2010', '12/31/2010'),
        ...                    'data': np.random.rand(365)})
        >>> df_formatted = rasterhydrograph.format_data(df, 'data', 'date')
        >>> df_formatted.index[0]
        2010
        >>> len(df_formatted.columns)
        365

    Formatting real daily data for a raster hydrograph.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="2000-01-01", end="2002-12-31")
        >>> df_formatted = rasterhydrograph.format_data(df, '00060_Mean')
        >>> df_formatted.index[0]
        2000
        >>> len(df_formatted.columns)
        365
    """
    # check inputs, set date to index, define year/doy columns
    df_out = _check_inputs(df, data_column_name, date_column_name,
                           data_type, year_type, begin_year, end_year,
                           clip_leap_day=clip_leap_day)

    # calculate the date range
    date_range = _calculate_date_range(df_out, year_type, begin_year, end_year)

    # format date_range as YYYY-MM-DD
    date_range = date_range.strftime('%Y-%m-%d')

    # set data type
    data_type = set_data_type(data_type)

    # make output data frame
    # calculation of rolling mean is done on the data column
    df_out = rolling_average(df_out, data_column_name, data_type, **kwargs)

    # convert date index to YYYY-MM-DD format
    df_out.index = df_out.index.strftime('%Y-%m-%d')

    # expand data frame to include all dates in date_range
    df_out = df_out.reindex(date_range)

    # convert date index to datetime format
    df_out.index = pd.to_datetime(df_out.index)

    # re-define year and doy columns
    df_out = define_year_doy_columns(df_out, year_type=year_type,
                                     clip_leap_day=clip_leap_day)
    # sort by date
    df_out = df_out.sort_index()

    # Incorporate leap year decision into x-axis labels
    if clip_leap_day:
        year = 1902
    else:
        year = 1903
    # Create x-axis scale and labels
    if year_type == 'water':
        month_day_order = pd.date_range(start=f'{year}-10-01', end=f'{year+1}-09-30').strftime('%m-%d')  # noqa: E501
    elif year_type == 'climate':
        month_day_order = pd.date_range(start=f'{year}-04-01', end=f'{year+1}-03-31').strftime('%m-%d')  # noqa: E501
    else:
        month_day_order = pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31').strftime('%m-%d')  # noqa: E501

    # set index to year and day of year columns
    df_out = df_out.pivot(index='index_year', columns='index_month_day',
                          values=data_column_name)
    # re-arrange columns by year_type
    df_out = df_out[month_day_order]

    # reverse order of the index so year order matches legacy Water Watch
    df_out = df_out.iloc[::-1]

    # remove all NaN columns and rows
    df_out = df_out.dropna(axis=1, how='all')
    df_out = df_out.dropna(axis=0, how='all')

    return df_out


def _check_inputs(df, data_column_name, date_column_name,
                  data_type, year_type, begin_year, end_year,
                  clip_leap_day):
    """Private function to check inputs for the format_data function.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    data_column_name : str
        The name of the column containing the data.
    date_column_name : str, None
        The name of the column containing the date or None if the index is
        the date.
    data_type : str
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.
    year_type : str
        The type of year to use. Must be one of 'calendar' or 'water'.
        'calendar' starts the year on January 1 and ends on
        December 31. 'water' starts the year on October 1 and ends on
        September 30.
    begin_year : int, None
        The first year to include in the data. If None, the first year in
        the data will be used.
    end_year : int, None
        The last year to include in the data. If None, the last year in the
        data will be used.
    clip_leap_day : bool, optional
        If True, removes leap day '02-29' from the percentiles dataset
        used to create the plot.

    Returns
    -------
    df : pandas.DataFrame
        The dataframe with the date column formatted as a datetime and set as
        the index. New year and doy (day of year) columns are added too and
        are set based on the year_type. Feb 29th is also removed from the
        dataframe if it exists.
    """
    # check the data frame
    if not isinstance(df, pd.DataFrame):
        raise TypeError('df must be a pandas.DataFrame')

    # check data type
    if not isinstance(data_type, str):
        raise TypeError('data_type must be a string')
    if data_type not in ['daily', '7-day', '14-day', '28-day']:
        raise ValueError('data_type must be one of "daily", "7-day", '
                         '"14-day", and "28-day"')

    # check data column name
    if not isinstance(data_column_name, str):
        raise TypeError('data_column_name must be a string')

    # check date column name
    if date_column_name is not None:
        if not isinstance(date_column_name, str):
            raise TypeError('date_column_name must be a string')

    # check begin year
    if begin_year is not None:
        if not isinstance(begin_year, int):
            raise TypeError('begin_year must be an integer')
        if date_column_name is not None:
            if begin_year < df['date'].dt.year.min():
                raise ValueError('begin_year must be greater than or equal to '
                                 'the minimum year in the data')
        else:
            if begin_year < df.index.year.min():
                raise ValueError('begin_year must be greater than or equal to '
                                 'the minimum year in the data')

    # check end year
    if end_year is not None:
        if not isinstance(end_year, int):
            raise TypeError('end_year must be an integer')
        if date_column_name is not None:
            if end_year > df['date'].dt.year.max():
                raise ValueError('end_year must be less than or equal to the '
                                 'maximum year in the data')
        else:
            if end_year > df.index.year.max():
                raise ValueError('end_year must be less than or equal to the '
                                 'maximum year in the data')

    # define year and doy columns and set index as date col if needed
    df = define_year_doy_columns(df, date_column_name, year_type,
                                 clip_leap_day=clip_leap_day)

    return df


def _calculate_date_range(df, year_type, begin_year, end_year):
    """Private function to calculate the date range and set the index.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    year_type : str
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'.
    begin_year : int, None
        The first year to include in the data. If None, the first year in
        the data will be used.
    end_year : int, None
        The last year to include in the data. If None, the last year in the
        data will be used.

    Returns
    -------
    date_range : pandas.DatetimeIndex
        The date range.
    """
    # set begin/end year if not provided
    if begin_year is None:
        begin_year = df.index.year.min()
    if end_year is None:
        end_year = df.index.year.max()
    # calendar year from Jan 1 to Dec 31
    if year_type == 'calendar':
        begin_date = pd.to_datetime(str(begin_year) + '-01-01')
        end_date = pd.to_datetime(str(end_year) + '-12-31')
    # water year from Oct 1 to Sep 30
    elif year_type == 'water':
        begin_date = pd.to_datetime(str(begin_year-1) + '-10-01')
        end_date = pd.to_datetime(str(end_year) + '-09-30')
    # climate year from Apr 1 to Mar 31
    elif year_type == 'climate':
        begin_date = pd.to_datetime(str(begin_year-1) + '-04-01')
        end_date = pd.to_datetime(str(end_year) + '-03-31')

    # set date range
    date_range = pd.date_range(begin_date, end_date)

    return date_range
