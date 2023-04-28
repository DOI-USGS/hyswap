"""Raster hydrograph functionality."""

import pandas as pd
from hyswap.utils import rolling_average


def format_data(df, data_column_name, date_column_name=None,
                data_type='daily', year_type='calendar',
                begin_year=None, end_year=None, **kwargs):
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
    # check inputs
    _check_inputs(df, data_column_name, date_column_name,
                  data_type, year_type, begin_year, end_year)

    # calculate the date range
    df, date_range = _calculate_date_range(df, begin_year, end_year,
                                           year_type, date_column_name)

    # format date_range as YYYY-MM-DD
    date_range = date_range.strftime('%Y-%m-%d')

    # set data type
    data_type = _set_data_type(data_type)

    # make output data frame
    # calculation of rolling mean is done on the data column
    df_out = rolling_average(df, data_column_name, data_type, **kwargs)

    # convert date index to YYYY-MM-DD format
    df_out.index = df_out.index.strftime('%Y-%m-%d')

    # fill in missing dates as nan values to complete the years
    df_out = df_out.reindex(index=date_range)

    # convert date index to datetime format
    df_out.index = pd.to_datetime(df_out.index)

    # organize data frame
    # rows are years and columns are days in the year

    # add day of year column
    df_out['day'] = df_out.index.dayofyear.copy()
    if year_type == 'water':
        # day 1 in a year becomes October 1
        # in a leap year October 1 is day 275
        df_out.loc[df_out.index.is_leap_year & (df_out.index.month >= 10),
                   'day'] -= 274
        # in a non-leap year, October 1 is day 274
        df_out.loc[~df_out.index.is_leap_year & (df_out.index.month >= 10),
                   'day'] -= 273
        # add dates for early days in year Jan 1 to Oct 1
        df_out.loc[df_out.index.month < 10, 'day'] += 92
    elif year_type == 'climate':
        # day 1 in a year becomes April 1
        # in a leap year April 1 is day 92
        df_out.loc[df_out.index.is_leap_year & (df_out.index.month >= 4),
                   'day'] -= 91
        # in a non-leap year, April 1 is day 91
        df_out.loc[~df_out.index.is_leap_year & (df_out.index.month >= 4),
                   'day'] -= 90
        # add dates for early days in year Jan 1 to April 1
        df_out.loc[df_out.index.month < 4, 'day'] += 275

    # add year column
    df_out['year'] = df_out.index.year.copy()
    if year_type == 'water':
        df_out.loc[df_out.index.month >= 10, 'year'] += 1
    elif year_type == 'climate':
        df_out.loc[df_out.index.month >= 4, 'year'] += 1

    # set index to year and day of year columns
    df_out = df_out.pivot(index='year', columns='day', values=data_column_name)

    # reverse order of the index so year order matches legacy Water Watch
    df_out = df_out.iloc[::-1]

    return df_out


def _check_inputs(df, data_column_name, date_column_name,
                  data_type, year_type, begin_year, end_year):
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

    Returns
    -------
    None
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

    # check year type
    if not isinstance(year_type, str):
        raise TypeError('year_type must be a string')
    if year_type not in ['calendar', 'water', 'climate']:
        raise ValueError('year_type must "calendar", "water", or "climate"')

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

    return None


def _calculate_date_range(df, begin_year, end_year, year_type,
                          date_column_name):
    """Private function to calculate the date range and set the index.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to format. Must have a date column or the index must be the
        date values.
    begin_year : int, None
        The first year to include in the data. If None, the first year in
        the data will be used.
    end_year : int, None
        The last year to include in the data. If None, the last year in the
        data will be used.
    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".
    date_column_name : str, None
        The name of the column containing the date or None if the index is
        the date.

    Returns
    -------
    df : pandas.DataFrame
        The data with the date range set as the index.
    date_range : pandas.DatetimeIndex
        The date range.
    """
    # set date column as index
    if date_column_name is not None:
        df = df.set_index(date_column_name)

    # set begin year
    if begin_year is None:
        if year_type == 'calendar':
            begin_year = df.index.year.min()
        elif year_type == 'water':
            if df.index[0].month < 10:
                begin_year = df.index.year.min()
            else:
                begin_year = df.index.year.min() + 1
        elif year_type == 'climate':
            if df.index[0].month < 4:
                begin_year = df.index.year.min()
            else:
                begin_year = df.index.year.min() + 1

    # set end year
    if end_year is None:
        if year_type == 'calendar':
            end_year = df.index.year.max()
        elif year_type == 'water':
            if df.index[-1].month >= 10:
                end_year = df.index.year.max() + 1
            else:
                end_year = df.index.year.max()
        elif year_type == 'climate':
            if df.index[-1].month >= 4:
                end_year = df.index.year.max() + 1
            else:
                end_year = df.index.year.max()

    # set date range
    if year_type == 'calendar':
        date_range = pd.date_range(f'{begin_year}-01-01',
                                   f'{end_year}-12-31')
    elif year_type == 'water':
        date_range = pd.date_range(f'{begin_year}-10-01',
                                   f'{end_year}-09-30')
    elif year_type == 'climate':
        date_range = pd.date_range(f'{begin_year}-04-01',
                                   f'{end_year}-03-31')

    return df, date_range


def _set_data_type(data_type):
    """Private function to set the data type.

    Parameters
    ----------
    data_type : str
        The type of data. Must be one of 'daily', '7-day', '14-day', and
        '28-day'. If '7-day', '14-day', or '28-day' is
        specified, the data will be averaged over the specified period. NaN
        values will be used for any days that do not have data. If present,
        NaN values will result in NaN values for the entire period.

    Returns
    -------
    data_type : str
        The formatted frequency string to be used with
        pandas.DataFrame.rolling to calculate the average over the correct
        temporal period.
    """
    if data_type == 'daily':
        data_type = 'D'
    elif data_type == '7-day':
        data_type = '7D'
    elif data_type == '14-day':
        data_type = '14D'
    elif data_type == '28-day':
        data_type = '28D'

    return data_type
