
Flow Duration Curve Examples
----------------------------

These examples show how flow duration curves can be constructed by fetching data from NWIS using `dataretrieval`, analyzing that data using functions provided by `hyswap` (:obj:`hyswap.exceedance.calculate_exceedance_probability_from_values_multiple`), and then plotted using `matplotlib`.
For more information on flow duration curves, see the USGS report titled "Flow-duration curves" by James K. Searcy and published in 1959 (https://doi.org/10.3133/wsp1542A).

First we will fetch all streamflow data for a single site from NWIS using the `dataretrieval` package.

.. plot::
    :context: reset
    :include-source:

    # get data from a single site
    siteno = '01646500'
    df, md = dataretrieval.nwis.get_dv(site=siteno, parameterCd='00060',
                                       startDT='1900-01-01')

This data can be filtered to only include "approved" data.
Data quality is coded as "A" for "approved" and "P" for "provisional".
`hyswap` has a utility function to help with this.

.. plot::
    :context:
    :include-source:

    # filter to only approved data
    df = hyswap.utils.filter_approved_data(df, '00060_Mean_cd')

Now we can calculate the exceedance probabilities for 10,000 evenly spaced values between the minimum and maximum values in the data.

.. plot::
    :context:
    :include-source:

    # generate 10,000 evenly spaced values between the min and max
    values = np.linspace(df['00060_Mean'].min(), df['00060_Mean'].max(), 10000)

    # calculate exceedance probabilities
    exceedance_probabilities = hyswap.exceedance.calculate_exceedance_probability_from_values_multiple(
        values, df['00060_Mean'])

Finally, we can plot the flow duration curve using these exceedance probability values and `matplotlib`.

.. plot::
    :context:
    :include-source:

    # plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(exceedance_probabilities * 100, values, linewidth=2)
    ax.set_xlabel(
        'Exceedance Probability\n' +
        '(Percent of Time Indicated Discharge was Equaled or Exceeded)')
    ax.set_ylabel('Discharge, ft$^3$/s')
    ax.set_title('Flow Duration Curve for Site # ' + siteno)
    # set log scales for axes
    ax.set_yscale('log')
    # set limits for axes
    ax.set_xlim(0.1, 99.9)
    ax.set_ylim(100, 1000000)
    # set ticks for axes
    ax.set_xticks([0.1, 5, 10, 25, 50, 75, 90, 95, 99.9])
    ax.set_xticklabels(['0.1', '5', '10', '25', '50', '75', '90', '95', '99.9'])
    ax.set_yticks([100, 1000, 10000, 100000, 1000000])
    ax.set_yticklabels(['100', '1,000', '10,000', '100,000', '1,000,000'])
    # add grid lines
    ax.grid(which='both', axis='both', alpha=0.5)
    # show the plot
    plt.tight_layout()
    plt.show()
