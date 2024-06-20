"""Runoff functions for hyswap."""
import pandas as pd
import numpy as np


def convert_cfs_to_runoff(cfs, drainage_area, frequency="annual"):
    """Convert cfs to runoff values for some drainage area.

    Parameters
    ----------
    cfs : float
        Flow in cubic feet per second.

    drainage_area : float
        Drainage area in km2.

    frequency : str, optional
        Frequency of runoff values to return. Options are 'annual',
        'monthly', and 'daily'. Default is 'annual'.

    Returns
    -------
    float
        Runoff in mm/<frequency>.

    Examples
    --------
    Convert 14 cfs to mm/yr for a 250 km2 drainage area.

    .. doctest::
        :skipif: True  # docstrings test fails with np.float64

        >>> mmyr = runoff.convert_cfs_to_runoff(14, 250)
        >>> np.round(mmyr)
        50.0
    """
    # convert frequency string to value
    if frequency == "annual":
        freq = 365.25
    elif frequency == "monthly":
        freq = 365.25 / 12
    elif frequency == "daily":
        freq = 1
    else:
        raise ValueError("Invalid frequency: {}".format(frequency))
    # convert cfs to cubic feet per frequency
    cpf = cfs * 60 * 60 * 24 * freq
    # convert cubic feet per freq to cubic meters per freq
    cpf = cpf * (0.3048 ** 3)
    # convert drainage area km2 to m2
    drainage_area = drainage_area * 1000 * 1000
    # convert cubic meters per year to mm per freq
    mmf = cpf / drainage_area * 1000
    return mmf


def streamflow_to_runoff(df, data_col, drainage_area, frequency="annual"):
    """Convert streamflow to runoff for a given drainage area.

    For a given gage/dataframe, convert streamflow to runoff using the
    drainage area and the convert_cfs_to_runoff function.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing streamflow data.

    data_col : str
        Column name containing streamflow data, assumed to be in cfs.

    drainage_area : float
        Drainage area in km2.

    frequency : str, optional
        Frequency of runoff values to return. Options are 'annual',
        'monthly', and 'daily'. Default is 'annual'.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing runoff data in a column named 'runoff'.

    Examples
    --------
    Convert streamflow to runoff for a given drainage area.

    .. doctest::

        >>> df = pd.DataFrame({'streamflow': [14, 15, 16]})
        >>> runoff_df = runoff.streamflow_to_runoff(df, 'streamflow', 250)
        >>> print(runoff_df['runoff'].round(1))
        0    50.0
        1    53.6
        2    57.2
        Name: runoff, dtype: float64
    """
    df['runoff'] = df[data_col].apply(
        lambda x: convert_cfs_to_runoff(x, drainage_area, frequency=frequency)
    )
    return df


def identify_sites_from_geom_intersection(
        geom_id,
        geom_intersection_df,
        geom_id_col,
        site_col,
        prop_geom_in_basin_col='prop_huc_in_basin',
        prop_basin_in_geom_col='prop_basin_in_huc'):

    """Identify sites for a specified geometry.

    Function to identify streamgage sites that have drainage areas
    intersecting a given spatial geometry (e.g. HUC8) from the
    output table of a previously computed spatial intersection
    of drainage areas and spatial geometries. This function is a
    helper function that can be used to reduce the number of NWIS
    queries that are performed to construct the list of dataframes
    for a given geometry.

    Parameters
    ----------
    geom_id : str
        Geometry ids to filter to (e.g. geom_id = '03030006').
        Ids range from 8 to 10 digits and sometime involve a leading 0.

    geom_intersection_df : pandas.DataFrame
        Tabular dataFrame containing columns indicating the site numbers,
        geometry ids, proportion of geometry in basin, and proportion
        of basin within geometry.

    geom_id_col : str
        Column in geom_intersection_df with geometry ids.

    site_col : str
        Column in geom_intersection_df with drainage area site numbers.
        Please make sure ids have the correct number of digits and have
        not lost leading 0s when read in. If the site numbers are the
        geom_intersection_df index col, site_col = 'index'.

    prop_geom_in_basin_col : str, optional
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'prop_huc_in_basin'

    prop_basin_in_geom_col : str, optional
        Name of column with values (type:float) representing the proportion
        (0 to 1)of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'prop_basin_in_huc'

    Returns
    -------
    list
        List of site IDs with drainage areas that intersect the geometry

    Examples
    --------
    Find all drainage area site numbers that intersect with geometry id 0101002

    .. doctest::

        >>> data = [['01014000', '01010002', 0.01, 0.6],
        ...     ['01014001', '01010002', 0.2, 0.8],
        ...     ['01014002', '01010003', 0.9, 0.05]]
        >>> df = pd.DataFrame(data,
        ... columns = ['site_no', 'geom_id', 'prop_huc_in_basin',
        ... 'prop_basin_in_huc'])
        >>> sites_lst = runoff.identify_sites_from_geom_intersection(
        ... geom_intersection_df=df, geom_id='01010002',
        ... geom_id_col='geom_id', site_col='site_no',
        ... prop_geom_in_basin_col='prop_huc_in_basin',
        ... prop_basin_in_geom_col='prop_basin_in_huc')
        >>> print(sites_lst)
        ['01014000', '01014001']
    """

    # Filter df to designated geometry (e.g. huc8)
    filtered_df = geom_intersection_df[
        geom_intersection_df[geom_id_col] == geom_id
        ]

    # Check whether sites is the df index or not
    if site_col == 'index':
        site_col = filtered_df.index
    else:
        site_col = filtered_df[site_col]

    # Retrieve all non-0 sites within the designated geometry (e.g. huc8)
    site_list = site_col[(filtered_df[prop_geom_in_basin_col] != 0) & (
        filtered_df[prop_basin_in_geom_col] != 0)].to_list()

    return site_list


def calculate_geometric_runoff(geom_id,
                               runoff_df,
                               geom_intersection_df,
                               site_col,
                               geom_id_col,
                               prop_geom_in_basin_col='prop_huc_in_basin',
                               prop_basin_in_geom_col='prop_basin_in_huc',
                               percentage=False,
                               clip_downstream_basins=True,
                               full_overlap_threshold=0.98):
    """Function to calculate the runoff for a specified geometry. Uses
    tabular dataframe containing proportion of geometry in each
    intersecting basin and proportion of intersecting basins in the
    specified geometry, as well as a dataframe of basin runoff values.
    Note that this function only calculates estimated runoff using
    intersecting basins with a complete runoff record over the
    entire date range of the dataframe. For this reason, the user
    may want to break up runoff calculations by month, year, or some
    other time step.

    Parameters
    ----------
    geom_id : str
        Geometry ID for the geometry of interest.

    runoff_df : pandas.DataFrame
        Dataframe containing runoff data for each site in the
        geometry. Dataframe is expected to have a date index entitled
        'datetime', a site id column entitled 'site_no', and a data
        column entitled 'runoff' filled with runoff data.

    geom_intersection_df : pandas.DataFrame
        Tabular dataFrame containing columns indicating the site numbers,
        geometry ids, proportion of geometry in basin, and proportion
        of basin within geometry.

    site_col : str
        Column in geom_intersection_df with drainage area site numbers.
        Please make sure ids have the correct number of digits and have
        not lost leading 0s when read in. If the site numbers are the
        geom_intersection_df index col, site_col = 'index'.

    geom_id_col : str
        Column in geom_intersection_df with geometry ids.

    prop_geom_in_basin_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'prop_in_basin'

    prop_basin_in_geom_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'prop_in_huc'

    percentage : boolean, optional
        If the values in geom_intersection_df are percentages,
        percentage = True. If the values are decimal proportions,
        percentage = False. Default: False

    clip_downstream_basins : boolean, optional
        When True, the function estimates runoff using only basins that are
        (a) contained within the geometry and (b) the smallest basin
        containing the geometry in the weighted average. When False,
        the function uses all overlapping basins to estimate runoff
        for the geometry. Defaults to True.

    full_overlap_threshold : float, optional
        The minimum proportion of overlap between geometry and basin that
        constitutes "full" overlap. For example, occasionally a geometry
        (or basin) may be completely contained by a basin (or geometry),
        but polygon border artifacts might cause the intersection to be
        slightly less than 1. This input accounts for that error.
        Defaults to 0.98.

    Returns
    -------
    pandas.DataFrame
        Dataframe containing the area-weighted runoff values for the geometry,
        as well as the number of sites used to generate the weight, the site
        ids, and the max weight for any site used in the weighting calculation.
    """
    # check if weights are percentage values
    if percentage is True:
        multiplier = 0.01
    else:
        multiplier = 1

    # check whether runoff_df contains sites not in geom_df
    # this might indicate mismatched format in site ids between
    # runoff_df and geom_intersection df
    check = list(set(runoff_df['site_no'].tolist()) - set(geom_intersection_df[site_col].tolist()))  # noqa: E501
    if check:
        print(('There are site ids in the runoff df that are not present '
               f'in the intersection df for {geom_id}. This might indicate '
               'a mismatch in site id formats, e.g. missing leading '
               'zeroes if NWIS sites.'))

    # check whether sites is the df index or not
    if site_col == 'index':
        geom_intersection_df = geom_intersection_df.reset_index()
        site_col = geom_intersection_df.columns[0]
        geom_intersection_df[site_col] = geom_intersection_df[site_col].astype(str)  # noqa: E501

    # assertion to check that site_col are not of type int
    assert geom_intersection_df[site_col].dtypes == 'str' or \
        geom_intersection_df[site_col].dtypes == 'object', 'geom_intersection_df site_col should be a str or obj'  # noqa: E501

    # filter intersction table to basins that overlap geom id
    filtered_intersection_df = geom_intersection_df[
        geom_intersection_df[geom_id_col] == geom_id
        ].copy()

    # filter weights df to sites with data in runoff_df
    sites = filtered_intersection_df[site_col]

    # get all site ids in runoff df
    ro_sites = runoff_df['site_no'].tolist()

    # grab sites that overlap between the intersection table
    # and runoff_df and filter runoff_df to those
    ro_sites = list(set(sites) & set(ro_sites))
    runoff_df = runoff_df[runoff_df['site_no'].isin(ro_sites)].reset_index()

    # pivot runoff_df to wide where each column represents
    # a site's runoff data and each row a datetime
    # and drop sites with incomplete data
    basin_runoff_wide = runoff_df.pivot(columns='site_no', index='datetime', values='runoff').dropna(axis='columns')  # noqa: E501

    if basin_runoff_wide.empty:
        print(f"No basins intersecting huc {geom_id} have a complete record in the dataset. Returning empty dataframe.")  # noqa: E501
        geom_runoff = pd.DataFrame()
        return geom_runoff

    # filter weights df to sites with data
    filtered_intersection_df = filtered_intersection_df[
        filtered_intersection_df[site_col].isin(basin_runoff_wide.columns.tolist())  # noqa: E501
        ]
    # check to see if empty
    if filtered_intersection_df.empty:
        print(('No runoff data available from intersecting sites to estimate '
               f'weighted runoff for {geom_id}. Check that your runoff '
               'df site_nos match site ids in your geom_intersection_df. '
               'Returning empty series.'))

    # remove any nans
    filtered_intersection_df = filtered_intersection_df.dropna(axis='rows')

    # converting proportions to decimals if applicable
    filtered_intersection_df[prop_geom_in_basin_col] = (filtered_intersection_df[prop_geom_in_basin_col] * multiplier)  # noqa: E501
    filtered_intersection_df[prop_basin_in_geom_col] = (filtered_intersection_df[prop_basin_in_geom_col] * multiplier)  # noqa: E501
    # calculate weight
    filtered_intersection_df['weight'] = filtered_intersection_df[prop_basin_in_geom_col] * filtered_intersection_df[prop_geom_in_basin_col]  # noqa: E501

    # check to see if there is overlap between geom and
    # basin(s) that is mutually > 0.9 * 0.9 (weight)
    geom_basin_overlap = filtered_intersection_df.loc[filtered_intersection_df['weight'] > (0.9 * 0.9)].copy()  # noqa: E501

    # if geom_basin_overlap is not empty, then the runoff is simply
    # the runoff from the basin with proportion overlap of > 0.9 AND
    # the highest weight.
    if not geom_basin_overlap.empty:
        geom_basin_overlap = geom_basin_overlap[geom_basin_overlap['weight'] == geom_basin_overlap['weight'].max()]  # noqa: E501
        geom_basin_overlap = geom_basin_overlap.head(1)
        # pick basin that has the highest weight: tightest overlap
        geom_runoff_series = runoff_df[runoff_df['site_no'] == geom_basin_overlap.iloc[0][site_col]].set_index('datetime').runoff  # noqa: E501
        # create new df with additional info about runoff calculations
        geom_runoff = pd.DataFrame(geom_runoff_series)
        geom_runoff = geom_runoff.rename(columns={'runoff': 'estimated_runoff'})  # noqa: E501
        geom_runoff['estimated_runoff'] = np.round(geom_runoff['estimated_runoff'], 5)  # noqa: E501
        geom_runoff['geom_id'] = geom_id
        geom_runoff['n_sites'] = 1
        geom_runoff['site_ids'] = geom_basin_overlap.iloc[0][site_col]
        geom_runoff['max_weight'] = np.round(geom_basin_overlap['weight'].max(), 4)  # noqa: E501
        geom_runoff['avg_weight'] = np.round(geom_basin_overlap['weight'].max(), 4)  # noqa: E501
        geom_runoff['max_site'] = geom_basin_overlap.iloc[0][site_col]
        return geom_runoff

    if clip_downstream_basins:
        # If return not executed, then go to the next step of
        # finding basins within the geom and the basin that contains
        # the geom with the largest weight
        # find where geom in basin is ~ 1 (contained by basin)
        geom_in_basin = filtered_intersection_df[(filtered_intersection_df[prop_geom_in_basin_col] > full_overlap_threshold)].copy()  # noqa: E501
        # if there are no basins containing the geometry object
        # with associated runoff data, let user know and then
        # check if there are any basins within geom.
        if geom_in_basin.empty:
            print(f"No runoff data associated with any basins containing the geometry object {geom_id} for the time period selected.")  # noqa: E501
        else:
            # grab basin with greatest weight value: this means it fully
            # contains the geom and closest in size to geom (a larger
            # basin would result in a smaller overall weight since the
            # proportion of the basin in geom would be smaller with a
            # bigger basin)
            geom_in_basin = geom_in_basin[geom_in_basin['weight'] == geom_in_basin['weight'].max()]  # noqa: E501
            # in case there are two or more basins with the same weight
            geom_in_basin = geom_in_basin.head(1)
            # make sure returns one value
            assert geom_in_basin.shape[0] == 1
        # grab all basins fully contained within the geom
        basin_in_geom = filtered_intersection_df[(filtered_intersection_df[prop_basin_in_geom_col] > full_overlap_threshold)].copy()  # noqa: E501
        # if there are no basins with runoff data, let user know.
        if basin_in_geom.empty:
            print(f"No runoff data associated with any basins contained within the geometry object {geom_id} for the time period selected.")  # noqa: E501
        # if both geom_in_basin and basin_in_geom are empty, meaning
        # no basins fully contain the huc and the huc doesn't fully
        # contain any basins, return empty series.
        if geom_in_basin.empty and basin_in_geom.empty:
            print(f"Insufficient data and/or overlap between basins and geometry object {geom_id}. Returning empty series.")  # noqa: E501
            return pd.Series(dtype='float32')
        # combine these two dfs into one
        else:
            final_geom_intersection_df = pd.concat(
                [geom_in_basin, basin_in_geom]
                )
    else:
        # Use all intersections to calculate a weighted average
        final_geom_intersection_df = filtered_intersection_df.copy()

    # subset to applicable basin runoff
    basins = final_geom_intersection_df[site_col].tolist()
    # ensure data df only has selected intersecting basins
    # and they are in the right order to apply weights
    basin_runoff_wide = basin_runoff_wide.filter(items=basins)[basins]
    # get number of sites and site id stats
    n_sites = basin_runoff_wide.shape[1]
    site_ids = ', '.join(basin_runoff_wide.columns)
    # calculate weighted runoff
    basin_runoff_wide['estimated_runoff'] = np.round(np.average(basin_runoff_wide,  # noqa: E501
                                                                weights=final_geom_intersection_df['weight'].to_numpy(),  # noqa: E501
                                                                axis=1), 5)
    basin_runoff = basin_runoff_wide.sort_index()
    # add geom_id, number of sites, site ids, and max weight to the output df
    basin_runoff['geom_id'] = geom_id
    basin_runoff['n_sites'] = n_sites
    basin_runoff['site_ids'] = site_ids
    basin_runoff['max_weight'] = np.round(final_geom_intersection_df['weight'].max(), 4)  # noqa: E501
    basin_runoff['avg_weight'] = np.round(final_geom_intersection_df['weight'].mean(), 4)  # noqa: E501
    basin_runoff['max_site'] = final_geom_intersection_df[site_col][final_geom_intersection_df['weight'].idxmax()]  # noqa: E501
    geom_runoff = basin_runoff[['geom_id', 'estimated_runoff', 'n_sites', 'site_ids', 'max_weight', 'avg_weight', 'max_site']]  # noqa: E501
    return geom_runoff


def calculate_multiple_geometric_runoff(
        geom_id_list,
        runoff_df,
        geom_intersection_df,
        site_col,
        geom_id_col,
        prop_geom_in_basin_col='prop_huc_in_basin',
        prop_basin_in_geom_col='prop_basin_in_huc',
        percentage=False,
        clip_downstream_basins=True,
        full_overlap_threshold=0.98
        ):
    """Calculate runoff for multiple geometries at once using
    `hyswap.calculate_geometric_runoff()`.
    Note that this function only calculates estimated runoff using
    intersecting basins with a complete runoff record over the
    entire date range of the dataframe. For this reason, the user
    may want to break up runoff calculations by month, year, or some
    other time step.

    Parameters
    ----------
    geom_id_list : list
        List of geometry ID strings for the geometries of interest.
        These should be columns in the weights matrix.

    runoff_df : pandas.DataFrame
        Dataframe containing runoff data for each site in the
        geometry. Dataframe is expected to have a date index entitled
        'datetime', a site id column entitled 'site_no', and a data
        column entitled 'runoff' filled with runoff data.

    geom_intersection_df : pandas.DataFrame
        Tabular dataFrame containing columns indicating the site numbers,
        geometry ids, proportion of geometry in basin, and proportion
        of basin within geometry.

    site_col : str
        Column in geom_intersection_df with drainage area site numbers.
        Please make sure ids have the correct number of digits
        and have not lost leading 0s when read in. If the site
        numbers are the geom_intersection_df index col, site_col = 'index'.

    geom_id_col : str
        Column in geom_intersection_df with geometry ids.

    prop_geom_in_basin_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the spatial geometry occurring in the corresponding
        drainage area. Default name: 'pct_in_basin'

    prop_basin_in_geom_col : str
        Name of column with values (type:float) representing the proportion
        (0 to 1) of the drainage area occurring in the corresponding
        spatial geometry. Default name: 'pct_in_huc'

    percentage : boolean, optional
        If the values in geom_intersection_df are percentages,
        percentage = True. If the values are decimal proportions,
        percentage = False. Default: False

    clip_downstream_basins : boolean, optional
        When True, the function estimates runoff using only basins that are
        (a) contained within the geometry and (b) the smallest basin
        containing the geometry in the weighted average. When False,
        the function uses all overlapping basins to estimate runoff
        for the geometry. Defaults to True.

    full_overlap_threshold : float, optional
        The minimum proportion of overlap between geometry and basin that
        constitutes "full" overlap. For example, occasionally a geometry
        (or basin) may be completely contained by a basin (or geometry),
        but polygon border artifacts might cause the intersection to be
        slightly less than 1. This input accounts for that error.
        Defaults to 0.98.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the area-weighted runoff values for each
        geometry, as well as the number of sites used to generate the
        weights, the site ids, and the max weight for any site used
        in the weighting calculation for each geometry.
    """
    # create empty dataframe to store results
    results_df = pd.DataFrame()
    # loop through geom_id_list to calculate runoff for each geometry
    for geom_id in geom_id_list:
        runoff_sites = identify_sites_from_geom_intersection(
            geom_id=geom_id,
            geom_intersection_df=geom_intersection_df,
            geom_id_col=geom_id_col,
            site_col=site_col,
            prop_geom_in_basin_col=prop_geom_in_basin_col,
            prop_basin_in_geom_col=prop_basin_in_geom_col
            )
        # subset df to sites with drainage areas that
        # intersect the geom_id
        geom_df = runoff_df.copy()
        geom_df = geom_df.loc[geom_df['site_no'].isin(runoff_sites)]
        if not geom_df.empty:
            print(geom_id)
            # calculate runoff for geometry
            runoff = calculate_geometric_runoff(
                geom_id=geom_id,
                runoff_df=geom_df,
                geom_intersection_df=geom_intersection_df,
                site_col=site_col,
                geom_id_col=geom_id_col,
                prop_basin_in_geom_col=prop_basin_in_geom_col,
                prop_geom_in_basin_col=prop_geom_in_basin_col,
                percentage=percentage,
                clip_downstream_basins=clip_downstream_basins,
                full_overlap_threshold=full_overlap_threshold)
        else:
            runoff = pd.DataFrame()

        # add runoff to results_df
        results_df = pd.concat([results_df, runoff])
    return results_df
