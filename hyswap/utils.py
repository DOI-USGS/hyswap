"""Utility functions for hyswap."""
import pandas as pd
import numpy as np


def filter_approved_data(data, filter_column=None):
    """Filter a dataframe to only return approved "A" (or "A, e") data.

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

    Examples
    --------
    Filter synthetic data to only return approved data. First make some
    synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     'data': [1, 2, 3, 4, 5],
        ...     'approved': ['A', 'A, e', 'A', 'P', 'P']})
        >>> df.shape
        (5, 2)

    Then filter the data to only return approved data.

    .. doctest::

        >>> df = utils.filter_approved_data(df, filter_column='approved')
        >>> df.shape
        (3, 2)
    """
    if filter_column is None:
        raise ValueError("filter_column must be specified.")
    return data[data[filter_column].str.contains("A", na=False)]


def rolling_average(df, data_column_name, data_type,
                    auto_min_periods=True, custom_min_periods=None,
                    **kwargs):
    """Calculate a rolling average for a dataframe.

    Default behavior right-aligns the window used for the rolling average
    and uses the data_type argument ('1D', '7D', '14D', '28D') to set the
    `min_periods` argument in `pandas.DataFrame.rolling`. The function
    returns NaN values if any of the values in the window are NaN or if the
    `mind_periods` argument is not satisifed. Properties of the windowing
    can be changed by passing additional keyword arguments which are fed
    to `pandas.DataFrame.rolling`.

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
    auto_min_periods : bool
        Defaults to True. When True, the `min_periods` argument in
        `pandas.DataFrame.rolling` is set using the `data_type` argument.
        For example, if the `data_type` = '7D', the `min_periods`
        argument is 7. When False, the `min_periods` argument is set
        using the `custom_min_periods` input.
    custom_min_periods : int, optional
        Defaults to None. Only used if `auto_min_periods` is False.
        If `auto_min_periods` is False and an integer is provided,
        that integer will be used to define the `min_periods` argument
        in `pandas.DataFrame.rolling`.
    **kwargs
        Additional keyword arguments to be passed to
        `pandas.DataFrame.rolling`.

    Returns
    -------
    pandas.DataFrame
        The output dataframe with the rolling average values.
    """
    if auto_min_periods is True:
        min_periods = pd.to_timedelta(data_type).days
    else:
        min_periods = custom_min_periods
    df_out = df.copy(deep=True)
    df_out[data_column_name] = df_out[data_column_name].rolling(
        data_type,
        min_periods, **kwargs).mean().round(2)
    return df_out


def filter_data_by_time(df, value, data_column_name, date_column_name=None,
                        time_interval='day',
                        leading_values=0, trailing_values=0,
                        drop_na=False):
    """Filter data by some time interval.

    DataFrame containing data to filter. Expects datetime information to be
    available in the index or in a column named `date_column_name`. The
    returned `pandas.Series` object will have the datetimes for the specified
    time (day, month, year) as the index, and the corresponding data from the
    `data_column_name` column as the values.

    Parameters
    ----------
    value : int
        Time value to use for filtering; value can be a day of year (1-366),
        month (1-12), or year (4 digit year).

    data_column_name : str
        Name of column containing data to filter.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    time_interval : str, optional
        Time interval to filter by. Must be one of 'day', 'month', or 'year'.
        Default is 'day'.

    leading_values : int, optional
        Number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        Number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    drop_na : bool, optional
        Drop NA values within filtered data

    Returns
    -------
    data : pandas.Series
        Data from the specified day of year.

    Examples
    --------
    Filter some synthetic data by day of year. First make some synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     'data': [1, 2, 3, 4],
        ...     'date': pd.date_range('2019-01-01', '2019-01-04')})
        >>> df.shape
        (4, 2)

    Then filter the data to get data from day 1.

    .. doctest::

        >>> data = utils.filter_data_by_time(
        ...     df, 1, 'data', date_column_name='date')
        >>> data.shape
        (1,)

    Acquire and filter some real daily data to get all Jan. 1 data.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="2000-01-01", end="2003-01-05")
        >>> data = utils.filter_data_by_time(df, 1, '00060_Mean')
        >>> data.shape
        (4,)
    """
    # make date column the index if it is not already
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # check that time_interval is valid
    if time_interval not in ['day', 'month', 'year']:
        raise ValueError(
            'time_interval must be one of "day", "month", or "year".')
    if time_interval == 'day':
        if (leading_values == 0) and (trailing_values == 0):
            # grab data from the specified day of year
            dff = df.loc[df.index.dayofyear == value, data_column_name]
        else:
            # grab data from the specified day of year and include leading
            # and trailing values.
            # note that at the beginning and end of the year, this section
            # wraps backward and forward, respectively, to ensure it is
            # calculating percentiles from a full window.
            if value < (1 + leading_values):
                dff = df.loc[
                    (df.index.dayofyear >= value - leading_values) &
                    (df.index.dayofyear <= value + trailing_values) |
                    (df.index.dayofyear >= 366 - (leading_values - value)),
                    data_column_name]
            elif value > (366 - trailing_values):
                dff = df.loc[
                    (df.index.dayofyear >= value - leading_values) &
                    (df.index.dayofyear <= value + trailing_values) |
                    (df.index.dayofyear <= trailing_values - (366 - value)),
                    data_column_name]
            else:
                dff = df.loc[
                    (df.index.dayofyear >= value - leading_values) &
                    (df.index.dayofyear <= value + trailing_values),
                    data_column_name]
            # If there are not sufficient data to complete moving
            # window, return empty df
            if dff.shape[0] < (leading_values + trailing_values + 1):
                dff = pd.DataFrame([])
    elif time_interval == 'month':
        # grab data from the specified month
        dff = df.loc[df.index.month == value, data_column_name]
    elif time_interval == 'year':
        # grab data from the specified year
        dff = df.loc[df.index.year == value, data_column_name]
    if drop_na:
        dff = dff.dropna()
    # return data as a pandas Series where the index is the date
    return dff


def filter_data_by_month_day(df,
                             month_day,
                             data_column_name,
                             date_column_name=None,
                             leading_values=0,
                             trailing_values=0,
                             drop_na=False):
    """Function used to filter to a single month-day (alternate
    to filter_data_by_time)

    DataFrame containing data to filter. Expects datetime information to be
    available in the index or in a column named `date_column_name`. The
    returned `pandas.Series` object will have the datetimes for the specified
    time (day, month, year) as the index, and the corresponding data from the
    `data_column_name` column as the values.

    Parameters
    ----------
    month_day : string
        Time value to use for filtering in the format 'MM-DD'.

    data_column_name : str
        Name of column containing data to filter.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    leading_values : int, optional
        Number of leading values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    trailing_values : int, optional
        Number of trailing values to include in the output, inclusive.
        Default is 0, and parameter only applies to 'day' time_interval.

    drop_na : bool, optional
        Drop NA values within filtered data

    Returns
    -------
    data : pandas.Series
        Data from the specified month-day, plus any leading/trailing
        values.

    Examples
    --------
    Filter some synthetic data by day of year. First make some synthetic data.

    .. doctest::

        >>> df = pd.DataFrame({
        ...     'data': [1, 2, 3, 4],
        ...     'date': pd.date_range('2019-01-01', '2019-01-04')})
        >>> df.shape
        (4, 2)

    Then filter the data to get data from January 1st.

    .. doctest::

        >>> data = utils.filter_data_by_month_day(
        ...     df, '01-01', 'data', date_column_name='date')
        >>> data.shape
        (1,)

    Acquire and filter some real daily data to get all Jan. 1 data.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     start="2000-01-01", end="2003-01-05")
        >>> data = utils.filter_data_by_month_day(df, '01-01', '00060_Mean')
        >>> data.shape
        (4,)
    """
    # make date column the index if it is not already
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # convert month-day to month and day ints
    t_month, t_day = map(int, month_day.split('-'))
    # check that month is valid
    if t_month > 12:
        raise ValueError(
            'Month invalid. month_day input must be format MM-DD')
        # check that month is valid
    if t_day > 31:
        raise ValueError(
            'Day invalid. month_day input must be format MM-DD')
    # subset df by month-day input
    subset_df = df[(df.index.month == t_month) & (df.index.day == t_day)].copy()  # noqa: E501
    if (leading_values == 0) and (trailing_values == 0):
        dff = subset_df[data_column_name]
    else:
        # if leading and trailing values are not zero,
        # create a column to define the trailing and leading
        # values for each year in the dataset
        subset_df['lv'] = subset_df.index - pd.to_timedelta(leading_values, unit='D')  # noqa: E501
        subset_df['tv'] = subset_df.index + pd.to_timedelta(trailing_values, unit='D')  # noqa: E501
        # create empty dataframe to hold all data chunks from
        # each year
        date_ranges_df = pd.DataFrame()
        # loop through each date range row
        # grab data chunk and place it in
        # dataframe created above
        for _, row in subset_df.iterrows():
            start_date = pd.to_datetime(row['lv'])
            end_date = pd.to_datetime(row['tv'])
            rng = (df.index >= start_date) & (df.index <= end_date)
            if df.loc[rng].shape[0] == (leading_values + trailing_values + 1):
                date_ranges_df = pd.concat([date_ranges_df, df.loc[rng]])
            else:
                date_ranges_df = pd.concat([date_ranges_df, pd.DataFrame([])])
        if date_ranges_df.empty:
            dff = date_ranges_df
        else:
            dff = date_ranges_df[data_column_name]
    if drop_na:
        dff = dff.dropna()
    return dff


def calculate_metadata(data):
    """Calculate metadata for a series of data.

    Parameters
    ----------
    data : pandas.Series
        The data to calculate the metadata for. Expected to have a datetime
        index.

    Returns
    -------
    dict
        The calculated metadata which includes the number of years of data,
        the number of data points, any gaps in the data, and the start and end
        dates of the data, the number of 0 values, the number of NA values,
        as well as the number of low (typically low flow <= 0.01) values.
    """
    # initialize the metadata dictionary
    meta = {}
    # calculate the number of unique years of data
    meta["n_years"] = len(data.index.year.unique())
    # calculate the number of data points that are not nan
    meta["n_data"] = len(data.loc[~data.isna()])
    # calculate the number of gaps in the data - missing years
    expected_years = data.index.year.max() - data.index.year.min() + 1
    meta["n_missing_years"] = expected_years - meta["n_years"]
    # calculate the start and end dates of the data
    meta["start_date"] = data.index.min().strftime("%Y-%m-%d")
    meta["end_date"] = data.index.max().strftime("%Y-%m-%d")
    # calculate the number of 0 values
    meta["n_zeros"] = len(data.loc[data == 0])
    # calculate the number of nan values
    meta["n_nans"] = len(data.loc[data.isna()])
    # calculate the number of low values (below 0.01)
    meta["n_lows"] = len(data.loc[data <= 0.01])

    return meta


def define_year_doy_columns(df_in, date_column_name=None, year_type='calendar',
                            clip_leap_day=False):
    """Function to add year, day of year, and month-day columns to a DataFrame.

    Parameters
    ----------
    df_in : pandas.DataFrame
        DataFrame containing data to filter. Expects datetime information to be
        available in the index or in a column named `date_column_name`.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011".

    clip_leap_day : bool, optional
        If True, February 29 is removed from the DataFrame. Default is False.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with year, day of year, and month-day columns added. Also
        makes the date_column_name the index of the DataFrame.
    """
    # deep copy of the df before manipulating it
    df = df_in.copy(deep=True)
    # set the df index
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    # check that year_type is valid
    if year_type not in ['calendar', 'water', 'climate']:
        raise ValueError(
            'year_type must be one of "calendar", "water", or "climate".')
    # add year and day of year columns
    if year_type == 'calendar':
        df['index_year'] = df.index.year
        df['index_doy'] = df.index.dayofyear
    elif year_type == 'water':
        # set water years
        df['index_year'] = df.index.year.where(df.index.month < 10,
                                               df.index.year + 1)
        # get calendar day of year
        df['index_doy'] = df.index.dayofyear
        # adjust Oct 1 to be day 1 of water year for leap and non-leap years
        df.loc[df.index.is_leap_year & (df.index.month >= 10),
               'index_doy'] -= 274
        df.loc[~df.index.is_leap_year & (df.index.month >= 10),
               'index_doy'] -= 273
        # adjust Jan 1 accordingly for leap and non-leap years
        df.loc[df.index.month < 10, 'index_doy'] += 92
    elif year_type == 'climate':
        # set climate years
        df['index_year'] = df.index.year.where(df.index.month < 4,
                                               df.index.year + 1)
        # get calendar day of year
        df['index_doy'] = df.index.dayofyear
        # adjust Apr 1 to be day 1 of climate year for leap and non-leap years
        df.loc[df.index.is_leap_year & (df.index.month >= 4),
               'index_doy'] -= 91
        df.loc[~df.index.is_leap_year & (df.index.month >= 4),
               'index_doy'] -= 90
        # adjust Jan 1 to be day 276 of climate year for all years
        df.loc[df.index.month < 4, 'index_doy'] += 275
    # add month and day columns
    df['index_month_day'] = df.index.strftime('%m-%d')
    # clip leap year and adjustment
    if clip_leap_day:
        df = leap_year_adjustment(df, year_type=year_type)
    # sort the df by year and day of year
    df = df.sort_values(['index_year', 'index_doy'])
    return df


def leap_year_adjustment(df, year_type='calendar'):
    """Function to adjust leap year days in a DataFrame.

    Adjust for a leap year by removing February 29 from the DataFrame and
    adjusting the day of year values for the remaining days of the year
    if a 'doy_index' column is present.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing data to adjust. Expects datetime information to be
        available in the index and a column named 'doy' containing day of year.

    year_type : str, optional
        The type of year to use. Must be one of 'calendar', 'water', or
        'climate'. Default is 'calendar' which starts the year on January 1
        and ends on December 31. 'water' starts the year on October 1 and
        ends on September 30 of the following year which is the "water year".
        For example, October 1, 2010 to September 30, 2011 is "water year
        2011". 'climate' years begin on April 1 and end on March 31 of the
        following year, they are numbered by the ending year. For example,
        April 1, 2010 to March 31, 2011 is "climate year 2011". Please note
        that this input is used to adjust the day of year index when a leap
        day is removed. If the dataframe does not have a day of year index,
        this input is ignored.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with leap year days removed and day of year values adjusted.
    """
    df = df.loc[~((df.index.month == 2) & (df.index.day == 29))]
    if 'index_doy' in df.columns:
        if year_type == 'calendar':
            df.loc[df.index.is_leap_year & (df.index.month > 2),
                   'index_doy'] -= 1
        elif year_type == 'water':
            df.loc[df.index.is_leap_year &
                   (df.index.month > 2) &
                   (df.index.month < 10), 'index_doy'] -= 1
        elif year_type == 'climate':
            df.loc[df.index.is_leap_year &
                   (df.index.month > 2) &
                   (df.index.month < 4), 'index_doy'] -= 1
    return df


def munge_nwis_stats(df, include_metadata=True):
    """Function to munge and reformat NWIS statistics data.

    This is a utility function that exists to help munge NWIS percentile data
    served via the NWIS statistics web service. This function uses the output
    of nwis.get_stats() for daily data at a single site and for a single
    parameter code.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing NWIS statistics data retrieved from the statistics
        web service. Assumed to come in as a dataframe retrieved with a
        package like dataretrieval or similar.

    include_metadata : bool, optional
        If True, return additional columns from NWIS Stats Service including
        count, mean, water year of start of record, water year of end of record

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing munged and reformatted NWIS statistics data.
        Reformatting is to match the format created by
        calculate_variable_percentile_thresholds_by_day function.

    Examples
    --------
    Get some NWIS statistics data.

    .. doctest::

        >>> df, md = dataretrieval.nwis.get_stats(
        ...     "03586500", parameterCd="00060", statReportType="daily")

    Then apply the function to munge the data.

    .. doctest::

        >>> df = utils.munge_nwis_stats(df)
        >>> df.shape
        (366, 15)
    """
    # rename columns from NWIS Stats Service
    df.columns = df.columns.str.rstrip('_va')
    # Note that NWIS Stats Service begin and end years are water years.
    df.rename(columns={'count_nu': 'count', 'begin_yr': 'start_wy',
                       'end_yr': 'end_wy', 'day_nu': 'day',
                       'month_nu': 'month'},
              inplace=True)
    # Use a leap year as basis to have all possible days of year included
    df['year'] = 1904
    # construct date column
    df['date'] = pd.to_datetime(df[['day', 'month', 'year']])
    # set month-day as index
    df['month_day'] = df['date'].dt.strftime('%m-%d')
    df = df.set_index('month_day')

    df = df.drop(['agency_cd', 'site_no', 'parameter_cd', 'ts_id',
                  'loc_web_ds', 'month', 'day', 'year', 'max_va_yr',
                  'min_va_yr', 'date'], axis=1)

    # move max and additional metadata columns (if returned) to end
    if include_metadata:
        cols_to_move = ['max', 'mean', 'count', 'start_wy', 'end_wy']
    else:
        df = df.drop(['mean', 'count', 'start_wy', 'end_wy'], axis=1)
        cols_to_move = ['max']
    # New column order with columns to move at the end
    new_column_order = [col for col in df.columns if col not in cols_to_move] \
        + cols_to_move
    df = df.reindex(columns=new_column_order)

    return df


def calculate_summary_statistics(df, data_col="00060_Mean"):
    """
    Calculate summary statistics for a site.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing daily values for the site. Expected to be from
        `dataretrieval.nwis.get_dv()`, or similar.

    data_col : str, optional
        Name of the column in the dv_df DataFrame that contains the data of
        interest. Default is "00060_Mean" which is the mean daily discharge
        column.

    Returns
    -------
    summary_df : pandas.DataFrame
        DataFrame containing summary statistics for the site.

    Examples
    --------
    Get some NWIS data and apply the function to get the summary statistics.

    .. doctest::

        >>> df, _ = dataretrieval.nwis.get_dv(
        ...     "03586500", parameterCd="00060",
        ...     startDT="2010-01-01", endDT="2010-12-31")
        >>> summary_df = utils.calculate_summary_statistics(df)
        >>> summary_df.shape
        (8, 1)
        >>> print(summary_df)
                    Summary Statistics
        Site number           03586500
        Begin date          2010-01-01
        End date            2010-12-31
        Count                      365
        Minimum                   2.48
        Mean                    207.43
        Median                    82.5
        Maximum                 3710.0
    """
    # make dictionary
    summary_dict = {}
    # populate it
    # site number (assumes USGS site number format)
    summary_dict['Site number'] = str(int(df.at[df.index[0],
                                                'site_no'])).zfill(8)
    # dates
    summary_dict['Begin date'] = df.index.min().strftime('%Y-%m-%d')
    summary_dict['End date'] = df.index.max().strftime('%Y-%m-%d')
    # count
    summary_dict['Count'] = df[data_col].count()
    # minimum
    summary_dict['Minimum'] = df[data_col].min()
    # mean
    summary_dict['Mean'] = df[data_col].mean().round(2)
    # median
    summary_dict['Median'] = df[data_col].median()
    # maximum
    summary_dict['Maximum'] = df[data_col].max()

    # make dataframe
    summary_df = pd.DataFrame(summary_dict, index=[0])

    # transpose and set column name
    summary_df = summary_df.T
    summary_df.columns = ['Summary Statistics']

    # return dataframe
    return summary_df


def filter_to_common_time(df_list):
    """Filter a list of dataframes to common times based on index.

    This function takes a list of dataframes and filters them to only include
    the common times based on the index of the dataframes. This is necessary
    before comparing the timeseries and calculating statistics between two or
    more timeseries.

    Parameters
    ----------
    df_list : list
        List of pandas.DataFrame objects to filter to common times.
        DataFrames assumed to have date-time information in the index.
        Expect input to be the output from a function like
        dataretrieval.nwis.get_dv() or similar.

    Returns
    -------
    df_list : list
        List of pandas.DataFrame objects filtered to common times.
    n_obs : int
        Number of observations in the common time period.

    Examples
    --------
    Get some NWIS data.

    .. doctest::

            >>> df1, md1 = dataretrieval.nwis.get_dv(
            ...     "03586500", parameterCd="00060",
            ...     start="2018-12-15", end="2019-01-07")
            >>> df2, md2 = dataretrieval.nwis.get_dv(
            ...     "01646500", parameterCd="00060",
            ...     start="2019-01-01", end="2019-01-14")
            >>> type(df1)
            <class 'pandas.core.frame.DataFrame'>
            >>> type(df2)
            <class 'pandas.core.frame.DataFrame'>

    Filter the dataframes to common times.

    .. doctest::

            >>> df_list, n_obs = utils.filter_to_common_time([df1, df2])
            >>> df_list[0].shape
            (7, 3)
            >>> df_list[1].shape
            (7, 3)
    """
    # get the common index
    common_index = df_list[0].index
    for df in df_list:
        common_index = common_index.intersection(df.index)
    # filter the dataframes to the common index
    for i, df in enumerate(df_list):
        df_list[i] = df.loc[common_index]
    # get the number of observations
    n_obs = len(common_index)
    # return the list of dataframes
    return df_list, n_obs


def set_data_type(data_type):
    """Function to set the data type for rolling averages.

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
        data_type = '1D'
    elif data_type == '7-day':
        data_type = '7D'
    elif data_type == '14-day':
        data_type = '14D'
    elif data_type == '28-day':
        data_type = '28D'

    return data_type


def categorize_flows(df,
                     percentile_col,
                     date_column_name=None,
                     min_years=None,
                     percentile_df=None,
                     schema_name='NWD',
                     custom_schema=None):
    """Function to categorize streamflows based on percentile ranges

    This function assigns a category to each streamflow observation for a
    single site by comparing the estimated percentile to a schema of percentile
    ranges and associated category labels

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing percentile values for date(s) of interest for the
        site.

    percentile_col : str
        Name of the column in the DataFrame that contains the data of
        interest, in this case estimated streamflow percentile.

    date_column_name : str, optional
        Name of column containing date information. If None, the index of
        `df` is used.

    min_years : int, optional
        Minimum number of years of data required to calculate percentile
        thresholds for a given day of year. Default is None. Use of min_years
        setting requires that percentile_df be provided.

    percentile_df : pd.DataFrame
        DataFrame where columns are the percentile thresholds values and the
        values are stored in a row called "values". Typically generated by the
        `calculate_fixed_percentile_thresholds` or `munge_nwis_stats` functions
        but could be provided manually. Must be indexed by month_day and
        include `count` column that represents number of years of records for
        that day of year.

    schema_name : str, optional
        Name of the categorization schema that should be used to categorize
        streamflow. Default is "NWD" schema.

    custom_schema : dict, optional
        Python dictionary describing custom schema to use for categorizing
        streamflow based on percentiles. Required in dict is 'ranges', an array
        of percentile cut points and 'labels', a list of category labels that
        matches the number of bins represented by ranges. Optionally can
        include 'low_label' and 'high_label' which are category labels
        associated with the lowest and highest values in 'ranges',
        respectively. Additional optional keys include 'colors', 'low_color',
        and 'high_color' which specify a color palette that can be accessed in
        user created plots and maps. Default is None.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame with flow_cat column added.

    Examples
    --------
    Categorize streamflow based on calculated percentiles for streamflow
    records downloaded from NWIS.

    .. doctest::
        :skipif: True  # dataretrieval functions break CI pipeline

        >>> data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="1900-01-01", end="2021-12-31")
        >>> pcts_df = percentiles.calculate_variable_percentile_thresholds_by_day(  # noqa: E501
        ...     data, '00060_Mean',
        ...     percentiles=[0, 5, 10, 25, 75, 90, 95, 100],
        ...     method='linear')
        >>> new_data, _ = dataretrieval.nwis.get_dv(
        ...     "04288000", parameterCd="00060",
        ...     start="2022-05-01", end="2022-05-07")
        >>> new_percentiles = percentiles.calculate_multiple_variable_percentiles_from_values(  # noqa: E501
        ...     new_data, '00060_Mean', pcts_df)
        >>> new_percentiles = utils.categorize_flows(new_percentiles,
        ...     'est_pct', schema_name='NWD')
        >>> new_percentiles[['est_pct', 'flow_cat']].values
        [[13.62, 'Below normal'],
        [14.15, 'Below normal'],
        [14.29, 'Below normal'],
        [23.41, 'Below normal'],
        [27.44, 'Normal'],
        [16.2, 'Below normal'],
        [12.81, 'Below normal']]
    """

    if custom_schema is None:
        schema = retrieve_schema(schema_name)
    else:
        schema = custom_schema
    # set the df index
    if date_column_name is not None:
        df = df.set_index(date_column_name)
    df['flow_cat'] = pd.cut(df[percentile_col], schema['ranges'],
                            labels=schema['labels'],
                            include_lowest=True,
                            right=False)
    if "low_label" in schema:
        df['flow_cat'] = df['flow_cat'].cat.add_categories(schema['low_label'])
        df.loc[df[percentile_col] == schema['ranges'][0], 'flow_cat'] = schema['low_label']  # noqa: E501
        df['flow_cat'] = df['flow_cat'].cat.reorder_categories(
            [schema['low_label']] +
            df['flow_cat'].cat.categories[:-1].tolist())
    if "high_label" in schema:
        df['flow_cat'] = df['flow_cat'].cat.add_categories(schema['high_label'])  # noqa: E501
        df.loc[df[percentile_col] == schema['ranges'][-1], 'flow_cat'] = schema['high_label']  # noqa: E501

    if min_years is not None:
        if percentile_df is not None:
            if 'count' not in percentile_df.columns:
                raise ValueError("Percentile threshold dataframe must " +
                                 "include count column")
            # add month-day column
            df['month_day'] = df.index.strftime('%m-%d')
            # join count (num years column)
            df = pd.merge(df, percentile_df['count'], how="left",
                          left_on="month_day", right_index=True)
            # set days where min_years is > count to "Not Ranked"
            df['flow_cat'] = np.where(df['count'] < min_years,
                                      "Not Ranked",
                                      df['flow_cat'])
            df = df.drop(['month_day', 'count'], axis=1)
        else:
            raise ValueError("Percentile threshold dataframe must be " +
                             "provided when using min_years setting")

    if min_years is not None:
        if percentile_df is not None:
            # add month-day column
            df['month_day'] = df.index.strftime('%m-%d')
            # join count (num years column)
            df = pd.merge(df, percentile_df['count'], how="left",
                          left_on="month_day", right_index=True)
            # set days where min_years is > count to "Not Ranked"
            df['flow_cat'] = np.where(df['count'] < min_years,
                                      "Not Ranked",
                                      df['flow_cat'])
            df = df.drop(['month_day', 'count'], axis=1)
        else:
            raise ValueError("Percentile threshold dataframe must be provided when using min_years setting")  # noqa: E501

    return df


def retrieve_schema(schema_name):
    """Function used to retrieve the flow range categories given a schema name

    Parameters
    ----------
    schema_name : str
        Name of the categorization schema that should be used to categorize
        streamflow. Available options are 'NWD', 'WaterWatch,
        'WaterWatch_Drought', 'WaterWatch_Flood', 'WaterWatch_BrownBlue', and
        'NIDIS_Drought'.

    Returns
    -------
    schema : dict
        dictionary of flow ranges, category labels, and color palette

    Examples
    --------
    Retrieve the categorization schema 'NWD' to categorization flow similar to
    the USGS National Water Dashboard

    .. doctest::
        :skipif: True

        >>> schema = utils.retrieve_schema('NWD')
        >>> print(schema)
        {'ranges': [0, 10, 25, 76, 90, 100],
        'labels': ['Much below normal', 'Below normal', 'Normal',
            'Above normal', 'Much above normal'],
        'colors': ['#b24249', '#e8ac49', '#44f24e', '#5fd7d9', '#2641f1'],
        'low_label': 'All-time low for this day',
        'low_color': '#e82f3e',
        'high_label': 'All-time high for this day',
        'high_color': '#1f296b'}
    """
    if schema_name.lower() == 'nwd':
        schema = {'ranges': [0, 10, 25, 76, 90, 100],
                  'labels': ['Much below normal', 'Below normal', 'Normal',
                             'Above normal', 'Much above normal'],
                  'colors': ['#b24249', '#e8ac49', '#44f24e', '#5fd7d9',
                             '#2641f1'],
                  'low_label': 'All-time low for this day',
                  'low_color': '#e82f3e',
                  'high_label': 'All-time high for this day',
                  'high_color': "#1f296b"}
    elif schema_name.lower() == 'waterwatch':
        schema = {'ranges': [0, 10, 25, 75, 90, 100],
                  'labels': ['Low', 'Much below normal', 'Below normal',
                             'Normal', 'Above normal',
                             'Much above normal', 'High'],
                  'colors': ['#af2327', '#fda328', '#29fd2f', '#4aded0',
                             '#0b24fb'],
                  'low_label': 'Low',
                  'low_color': '#fc0d1b',
                  'high_label': 'High',
                  'high_color': "#000000"}
    elif schema_name.lower() == 'waterwatch_drought':
        schema = {'ranges': [0, 5, 10, 25],
                  'labels': ['Severe hydrologic drought',
                             'Moderate hydrologic drought',
                             'Below normal'],
                  'colors': ['#af2327', '#fd9941', '#fecb6e'],
                  'low_label': 'Extreme hydrologic drought',
                  'low_color': '#fc0d1b'}
    elif schema_name.lower() == 'waterwatch_flood':
        schema = {'ranges': [0, 95, 99, 101],
                  'labels': ['<95%',
                             '95-98%',
                             '>= 99%'],
                  'colors': ['#ffffff', '#4aded0', '#0b24fb']}
    elif schema_name.lower() == 'waterwatch_brownblue':
        schema = {'ranges': [0, 10, 25, 75, 90, 100],
                  'labels': ['Much below normal', 'Below normal',
                             'Normal', 'Above normal', 'Much above normal'],
                  'colors': ['#dcb668', '#ebd6ab', '#e9e9e9', '#aacee0',
                             '#5699c0'],
                  'low_label': 'Low',
                  'low_color': '#8f4f1f',
                  'high_label': 'High',
                  'high_color': "#292f6b"}
    elif schema_name.lower() == 'nidis_drought':
        schema = {'ranges': [0, 2, 5, 10, 20, 30],
                  'labels': ['Exceptional drought',
                             'Extreme drought',
                             'Severe drought',
                             'Moderate drought',
                             'Abnormally dry'],
                  'colors': ['#720206', '#e30b17', '#fda929', '#fbd285',
                             '#fffd38']}
    else:
        raise ValueError('no matching schema found for ' + schema_name)

    return schema
