"""Raster hydrograph functionality."""

import pandas as pd


def format_data(df, data_column_name, date_column_name=None,
                data_type='daily', year_type='calendar',
                begin_year=None, end_year=None):
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
        The type of year to use. Must be one of 'calendar' or 'water'.
        Default is 'calendar' which starts the year on January 1 and ends on
        December 31. 'water' starts the year on October 1 and ends on
        September 30.
    begin_year : int, optional
        The first year to include in the data. Default is None which uses the
        first year in the data.
    end_year : int, optional
        The last year to include in the data. Default is None which uses the
        last year in the data.

    Returns
    -------
    pandas.DataFrame
        The formatted data starting on the first day of the first year and
        ending on the last day of the last year with the specified data type
        and year type.

    Examples
    --------
    Formatting daily data for a raster hydrograph.

    .. todo:: Add example.

    """
    # check data type
    if data_type not in ['daily', '7-day', '14-day', '28-day']:
        raise ValueError('data_type must be one of "daily", "7-day", '
                         '"14-day", and "28-day"')

    # check year type
    if year_type not in ['calendar', 'water']:
        raise ValueError('year_type must be one of "calendar" and "water"')

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

    # set begin year
    if begin_year is None:
        if date_column_name is not None:
            begin_year = df['date'].dt.year.min()
        else:
            begin_year = df.index.year.min()

    # set end year
    if end_year is None:
        if date_column_name is not None:
            end_year = df['date'].dt.year.max()
        else:
            end_year = df.index.year.max()

    # set date range
    if year_type == 'calendar':
        date_range = pd.date_range(f'{begin_year}-01-01',
                                   f'{end_year}-12-31')
    elif year_type == 'water':
        date_range = pd.date_range(f'{begin_year}-10-01',
                                   f'{end_year}-09-30')

    # formate date_range as YYYY-MM-DD
    date_range = date_range.strftime('%Y-%m-%d')

    # set data type
    if data_type == 'daily':
        data_type = 'D'
    elif data_type == '7-day':
        data_type = '7D'
    elif data_type == '14-day':
        data_type = '14D'
    elif data_type == '28-day':
        data_type = '28D'

    # make output data frame
    # calculation of rolling mean is done on the data column
    df_out = df[data_column_name].rolling(
        data_type, center=True).mean().to_frame()

    # convert date index to YYYY-MM-DD format
    df_out.index = df_out.index.strftime('%Y-%m-%d')

    # fill in missing dates as nan values to complete the years
    df_out = df_out.reindex(index=date_range)

    # convert date index to datetime format
    df_out.index = pd.to_datetime(df_out.index)

    # organize data frame
    # rows are years and columns are days in the year
    # add year column
    df_out['year'] = df_out.index.year
    if year_type == 'water':
        df_out.loc[df_out.index.month < 10, 'year'] -= 1

    # add day of year column
    df_out['day'] = df_out.index.dayofyear
    if year_type == 'water':
        df_out.loc[df_out.index.month < 10, 'day'] += 274

    # set index to year and day of year columns
    df_out = df_out.pivot(index='year', columns='day', values=data_column_name)

    return df_out
