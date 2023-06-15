
Similarity Measures
-------------------

These examples showcase the usage of the functions in the `similarity` module, with heatmap visualizations via the :obj:`hyswap.plots.plot_similarity_heatmap` function.
Sometimes it is helpful to compare the relationships between a set of stations and their respective measurements.
The `similarity` functions packaged in `hyswap` handle some of the data clean-up for you by ensuring the time-series of observations being compared at the same, and by removing any missing data.
This ensures that your results are not skewed by missing data or gaps in one of the time-series.


Correlations Between 5 Stations
*******************************

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
    results = hyswap.similarity.calculate_correlations(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results,
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
    results = hyswap.similarity.calculate_correlations(df_list, "00060_Mean")

    # make plot
    ax = hyswap.plots.plot_similarity_heatmap(
        results,
        title="Pearson Correlation Coefficients for Streamflow\n" +
              "Between 5 Sites Along the Mississippi River",
        show_values=True)

    # show the plot
    plt.tight_layout()
    plt.show()
