"""Similarity measures for hyswap."""

import numpy as np
import pandas as pd
from scipy import stats
from hyswap.utils import filter_to_common_time


def calculate_correlations(df_list, data_column_name, df_names=None):
    """Calculate Pearson correlations between dataframes in df_list.

    This function is designed to calculate the Pearson correlation
    coefficients between dataframes in df_list. The dataframes in df_list are
    expected to have the same columns. The correlation coefficients are
    calculated using the `numpy.corrcoeff` function.

    Parameters
    ----------
    df_list : list
        List of dataframes. The dataframes are expected to have the same
        columns. Likely inputs are the output of a function like
        dataretrieval.nwis.get_dv() or similar

    data_column_name : str
        Name of the column to use for the correlation calculation.

    df_names : list, optional
        List of names for the dataframes in df_list. If provided, the names
        will be used to label the rows and columns of the output array. If
        not provided, the column "site_no" will be used if available, if it is
        not available, the index of the dataframe in the list will be used.

    Returns
    -------
    correlations : pandas.DataFrame
        Dataframe of correlation coefficients. The rows and columns are
        labeled with the names of the dataframes in df_list as provided
        by df_names argument.

    n_obs : int
        Number of observations used to calculate the energy distance.

    Examples
    --------
    Calculate correlations between two synthetic dataframes.

    .. doctest::

        >>> df1 = pd.DataFrame({'a': np.arange(10), 'b': np.arange(10)})
        >>> df2 = pd.DataFrame({'a': -1*np.arange(10), 'b': np.arange(10)})
        >>> results, n_obs = similarity.calculate_correlations([df1, df2], 'a')
        >>> results
             0    1
        0  1.0 -1.0
        1 -1.0  1.0
    """
    # handle the names of the dataframes
    df_names = _name_handling(df_list, df_names)
    # preprocess dataframe list so they have the same index/times
    df_list, n_obs = filter_to_common_time(df_list)
    # calculate correlations between all pairs of dataframes in the list
    correlations = np.empty((len(df_list), len(df_list)))
    for i, df1 in enumerate(df_list):
        for j, df2 in enumerate(df_list):
            correlations[i, j] = np.corrcoef(
                df1[data_column_name], df2[data_column_name])[0, 1]
    # turn the correlations into a dataframe
    correlations = pd.DataFrame(
        correlations, index=df_names, columns=df_names)
    return correlations, n_obs


def calculate_wasserstein_distance(df_list, data_column_name, df_names=None):
    """Calculate Wasserstein distance between dataframes in df_list.

    This function is designed to calculate the Wasserstein distance between
    dataframes in df_list. The dataframes in df_list are expected to have the
    same columns. The Wasserstein distance is calculated using the
    `scipy.stats.wasserstein_distance` function.

    Parameters
    ----------
    df_list : list
        List of dataframes. The dataframes are expected to have the same
        columns. Likely inputs are the output of a function like
        dataretrieval.nwis.get_dv() or similar

    data_column_name : str
        Name of the column to use for the Wasserstein distance calculation.

    df_names : list, optional
        List of names for the dataframes in df_list. If provided, the names
        will be used to label the rows and columns of the output array. If
        not provided, the column "site_no" will be used if available, if it is
        not available, the index of the dataframe in the list will be used.

    Returns
    -------
    wasserstein_distances : pandas.DataFrame
        Dataframe of Wasserstein distances. The rows and columns are
        labeled with the names of the dataframes in df_list as provided
        by df_names argument.

    n_obs : int
        Number of observations used to calculate the energy distance.

    Examples
    --------
    Calculate Wasserstein distances between two synthetic dataframes.

    .. doctest::

        >>> df1 = pd.DataFrame({'a': np.arange(10), 'b': np.arange(10)})
        >>> df2 = pd.DataFrame({'a': -1*np.arange(10), 'b': np.arange(10)})
        >>> results, n_obs = similarity.calculate_wasserstein_distance(
        ...     [df1, df2], 'a')
        >>> results
             0    1
        0  0.0  9.0
        1  9.0  0.0
    """
    # handle the names of the dataframes
    df_names = _name_handling(df_list, df_names)
    # preprocess dataframe list so they have the same index/times
    df_list, n_obs = filter_to_common_time(df_list)
    # calculate distances between all pairs of dataframes in the list
    wasserstein_distances = np.empty((len(df_list), len(df_list)))
    for i, df1 in enumerate(df_list):
        for j, df2 in enumerate(df_list):
            wasserstein_distances[i, j] = stats.wasserstein_distance(
                df1[data_column_name], df2[data_column_name])
    # handle the names of the dataframes
    df_names = _name_handling(df_list, df_names)
    # turn the distances into a dataframe
    wasserstein_distances = pd.DataFrame(
        wasserstein_distances, index=df_names, columns=df_names)
    return wasserstein_distances, n_obs


def calculate_energy_distance(df_list, data_column_name, df_names=None):
    """Calculate energy distance between dataframes in df_list.

    This function is designed to calculate the energy distance between
    dataframes in df_list. The dataframes in df_list are expected to have the
    same columns. The energy distance is calculated using the
    `scipy.stats.energy_distance` function.

    Parameters
    ----------
    df_list : list
        List of dataframes. The dataframes are expected to have the same
        columns. Likely inputs are the output of a function like
        dataretrieval.nwis.get_dv() or similar

    data_column_name : str
        Name of the column to use for the energy distance calculation.

    df_names : list, optional
        List of names for the dataframes in df_list. If provided, the names
        will be used to label the rows and columns of the output array. If
        not provided, the column "site_no" will be used if available, if it is
        not available, the index of the dataframe in the list will be used.

    Returns
    -------
    energy_distances : pandas.DataFrame
        Dataframe of energy distances. The rows and columns are
        labeled with the names of the dataframes in df_list as provided
        by df_names argument.

    n_obs : int
        Number of observations used to calculate the energy distance.

    Examples
    --------
    Calculate energy distances between two synthetic dataframes.

    .. doctest::

        >>> df1 = pd.DataFrame({'a': np.arange(10), 'b': np.arange(10)})
        >>> df2 = pd.DataFrame({'a': -1*np.arange(10), 'b': np.arange(10)})
        >>> results, n_obs = similarity.calculate_energy_distance(
        ...     [df1, df2], 'a')
        >>> results
                  0         1
        0  0.000000  3.376389
        1  3.376389  0.000000
    """
    # handle the names of the dataframes
    df_names = _name_handling(df_list, df_names)
    # preprocess dataframe list so they have the same index/times
    df_list, n_obs = filter_to_common_time(df_list)
    # calculate distances between all pairs of dataframes in the list
    energy_distances = np.empty((len(df_list), len(df_list)))
    for i, df1 in enumerate(df_list):
        for j, df2 in enumerate(df_list):
            energy_distances[i, j] = stats.energy_distance(
                df1[data_column_name], df2[data_column_name])
    # handle the names of the dataframes
    df_names = _name_handling(df_list, df_names)
    # turn the distances into a dataframe
    energy_distances = pd.DataFrame(
        energy_distances, index=df_names, columns=df_names)
    return energy_distances, n_obs


def _name_handling(df_list, df_names):
    """Private function to handle the names of the dataframes."""
    if df_names is None:
        df_names = []
        for i, df in enumerate(df_list):
            if 'site_no' in df.columns:
                df_names.append(df['site_no'].iloc[0])
            else:
                df_names.append(str(i))
    return df_names
