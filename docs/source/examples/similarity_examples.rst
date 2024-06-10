
Similarity Measures
-------------------

Sometimes it is helpful to compare the relationships between a set of streamgaging stations and their respective measurements. These examples showcase the usage of the functions in the `similarity` module to quantify how similar streamflow records are across multiple streamgages. Matrices of similarity measures (e.g., correlations) are calculated and visualized by generating heatmap visualizations via the :obj:`hyswap.plots.plot_similarity_heatmap` function.

The `similarity` functions packaged in `hyswap` handle some of the data clean-up for you by ensuring the time-series of observations being compared acros the same dates, and by removing any missing data. This ensures that your results are not skewed by missing data or gaps in one of the time-series.


Pearson's *r* Correlations Between 5 Stations
*********************************************

The following example shows the correlations between streamflow at 5 stations (07374525, 07374000, 07289000, 07032000, 07024175) along the Mississippi River, listed from downstream to upstream.
First we have to fetch the streamflow data for these stations, to do this we will use the `dataretrieval` package to access the NWIS database.

.. plot::
    :context: reset
    :include-source:

    # get the data from these 5 sites
    site_list = ["07374525", "07374000", "07289000", "07032000", "07024175"]

    # fetch some streamflow data from NWIS as a list of dataframes
    df_list = []
    for site in site_list:
        df, _ = dataretrieval.nwis.get_dv(site, start="2012-01-01",
                                          end="2022-12-31",
                                          parameterCd='00060')
        df_list.append(df)

Once we've collected the streamflow data, we will calculate the pair-wise correlations between the stations using the :obj:`hyswap.similarity.calculate_correlations` function and then plot the results using :obj:`hyswap.plots.plot_similarity_heatmap`.

.. plot::
    :context:
    :include-source:

    # calculate correlations
    results, n_obs = hyswap.similarity.calculate_correlations(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results, n_obs=n_obs,
        title="Pearson Correlation Coefficients for Streamflow\n" +
              "Between 5 Sites Along the Mississippi River")

    # show the plot
    plt.tight_layout()
    plt.show()

If we'd like, we can display the specific values of the correlations by setting the `show_values` argument to `True` in the :obj:`hyswap.plots.plot_similarity_heatmap` function.

.. plot::
    :context: reset
    :include-source:

    # get the data from these 5 sites
    site_list = ["07374525", "07374000", "07289000", "07032000", "07024175"]

    # fetch some streamflow data from NWIS as a list of dataframes
    df_list = []
    for site in site_list:
        df, _ = dataretrieval.nwis.get_dv(site, start="2012-01-01",
                                          end="2022-12-31",
                                          parameterCd='00060')
        df_list.append(df)

    # calculate correlations
    results, n_obs = hyswap.similarity.calculate_correlations(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results, n_obs=n_obs,
        title="Pearson Correlation Coefficients for Streamflow\n" +
              "Between 5 Sites Along the Mississippi River",
        show_values=True)

    # show the plot
    plt.tight_layout()
    plt.show()


Wasserstein Distances Between 5 Stations
****************************************

In this example we compare the same 5 time-series as the previous example, but instead of calculating correlations, we calculate the `Wasserstein Distance <https://en.wikipedia.org/wiki/Wasserstein_metric>`_ between each pairing of time-series.
The Wasserstein Distance is a measure of the distance between two probability distributions, in this case the probability distributions of the streamflow values at each station.
Specifically in `hyswap`, we utilize the `scipy.stats.wasserstein_distance()` function, and are therefore specifically calculating the "first" Wasserstein Distance between two time-series.

.. plot::
    :context: reset
    :include-source:

    # get the data from these 5 sites
    site_list = ["07374525", "07374000", "07289000", "07032000", "07024175"]

    # fetch some streamflow data from NWIS as a list of dataframes
    df_list = []
    for site in site_list:
        df, _ = dataretrieval.nwis.get_dv(site, start="2012-01-01",
                                          end="2022-12-31",
                                          parameterCd='00060')
        df_list.append(df)

    # calculate Wasserstein Distances
    results, n_obs = hyswap.similarity.calculate_wasserstein_distance(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results, n_obs=n_obs,
        title="Wasserstein Distances for Streamflow\n" +
              "Between 5 Sites Along the Mississippi River",
        show_values=True)

    # show the plot
    plt.tight_layout()
    plt.show()


Energy Distances Between 5 Stations
***********************************

In this example we compare the same 5 time-series as the previous example, but this time using another distance measure, the so-called `Energy Distance <https://en.wikipedia.org/wiki/Energy_distance>`_ between two time-series.
The `energy_dist` is a statistical distance between two probability distributions, in this case the probability distributions of the streamflow values at each station.
Specifically in `hyswap`, we utilize the `scipy.stats.energy_distance()` function.

.. plot::
    :context: reset
    :include-source:

    # get the data from these 5 sites
    site_list = ["07374525", "07374000", "07289000", "07032000", "07024175"]

    # fetch some streamflow data from NWIS as a list of dataframes
    df_list = []
    for site in site_list:
        df, _ = dataretrieval.nwis.get_dv(site, start="2012-01-01",
                                          end="2022-12-31",
                                          parameterCd='00060')
        df_list.append(df)

    # calculate Wasserstein Distances
    results, n_obs = hyswap.similarity.calculate_energy_distance(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results, n_obs=n_obs,
        title="Energy Distances for Streamflow\n" +
              "Between 5 Sites Along the Mississippi River",
        show_values=True)

    # show the plot
    plt.tight_layout()
    plt.show()
