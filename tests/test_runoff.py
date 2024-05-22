"""Tests for the runoff.py module."""
import pytest
from hyswap import runoff
import numpy as np
import pandas as pd


def test_convert_cfs_to_runoff():
    """Test the convert_cfs_to_runoff function."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250)
    assert pytest.approx(mmyr, 0.1) == 50.0


def test_convert_cfs_to_runoff_annual():
    """Test the convert_cfs_to_runoff function with annual kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='annual')
    assert pytest.approx(mmyr, 0.1) == 50.0


def test_convert_cfs_to_runoff_monthly():
    """Test the convert_cfs_to_runoff function with monthly kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='monthly')
    assert pytest.approx(mmyr, 0.1) == 4.2


def test_convert_cfs_to_runoff_daily():
    """Test the convert_cfs_to_runoff function with daily kwarg."""
    mmyr = runoff.convert_cfs_to_runoff(14, 250, frequency='daily')
    assert pytest.approx(mmyr, 0.1) == 0.14


def test_convert_cfs_to_runoff_invalid():
    """Test the convert_cfs_to_runoff function with invalid kwarg."""
    with pytest.raises(ValueError):
        runoff.convert_cfs_to_runoff(14, 250, frequency='invalid')


def test_streamflow_to_runoff():
    """Test the streamflow_to_runoff function."""
    df = pd.DataFrame({"streamflow": [14, 15, 16]})
    runoff_df = runoff.streamflow_to_runoff(df, "streamflow", 250)
    assert pytest.approx(runoff_df["runoff"].round(1)) == [50.0, 53.6, 57.2]


@pytest.fixture
def weight_matrix():
    """Load and then return the demo weights matrix df as a test fixture."""
    return pd.read_json("tests/demo_weights.json")


@pytest.fixture
def weight_table():
    """Load and then return the demo weights tabular df as a test fixture."""
    return pd.read_csv("tests/demo_weights_table.csv",
                       converters={0: str, 1: str})


@pytest.fixture
def df_list(weight_matrix):
    """Create a synthetic list of dataframes as a test fixture."""
    siteids = weight_matrix.index.tolist()
    df_list = []
    for siteid in siteids:
        df = pd.DataFrame({
            "site_no": [siteid, siteid, siteid],
            "runoff": list(np.random.random(3))
        })
        df.index = pd.date_range(
            "2000-01-01", periods=3, freq="D").tz_localize("UTC")
        df_list.append(df)
    return df_list


def test_identify_sites_from_geom_intersection(weight_table):
    """Test the identify_sites_from_geom_intersection function."""
    siteids = runoff.identify_sites_from_geom_intersection(
        geom_id="05090201",
        geom_intersection_df=weight_table,
        geom_id_col='huc_cd',
        site_col='site_no',
        prop_geom_in_basin_col='pct_in_basin',
        prop_basin_in_geom_col='pct_in_huc')

    assert siteids == ['03234300']


class TestCalculateGeometricRunoff:
    # data for all tests in this class
    # HUC A - perfect overlap example
    # HUC B - huc within and basin within example
    # HUC C - two basins contain huc, so test different methods
    # HUC D - basin contained within huc
    # HUC E - no runoff data
    # HUC F - missing intersection info
    # HUC G - nan runoff value
    geom_intersection = pd.DataFrame({
        'site_id': ['01', '02', '03', '04',
                    '05', '06', '07', '08',
                    '09', '010', '011', '012',
                    '013', '014', '015'],
        'huc_id': ['A', 'A', 'A', 'B', 'B',
                   'B', 'C', 'C', 'C', 'D',
                   'E', 'F', 'F', 'G', 'G'],
        'prop_huc_in_basin': [0.98, 0.5, 0.1, 0.99,
                              0.5, 0.3, 0.99, 0.99,
                              0.01, 0.15, 0.98, np.nan,
                              0.98, 0.99, 0.2],
        'prop_basin_in_huc': [0.98, 0.3, 0.2, 0.6,
                              0.99, 0.1, 0.6, 0.1,
                              0.01, 0.99, 0.99, 0.99,
                              0.7, 0.3, 0.99]
    })
    geom_intersection_perc = geom_intersection.copy()
    geom_intersection_perc['perc_huc_in_basin'] = geom_intersection_perc['prop_huc_in_basin']*100  # noqa: E501
    geom_intersection_perc['perc_basin_in_huc'] = geom_intersection_perc['prop_basin_in_huc']*100  # noqa: E501
    keys = [f'0{i}' for i in range(1, 16)]
    runoff_df = pd.DataFrame()
    for key in keys:
        df = pd.DataFrame({
            'site_no': key,
            'runoff': np.random.random(len(pd.date_range('2023-01-01', '2023-01-04'))),  # noqa: E501
            'datetime': pd.date_range('2023-01-01', '2023-01-04')
            }).set_index('datetime')
        runoff_df = pd.concat([runoff_df, df])
    runoff_df = runoff_df.loc[~(runoff_df['site_no'] == '011')]
    reset = runoff_df.loc[runoff_df['site_no'] == '014'].runoff[3]
    runoff_df['runoff'] = runoff_df['runoff'].replace({reset: np.nan})

    def test_calculate_geometric_runoff_complete_overlap(self):
        """Test runoff function with huc overlapping basin."""
        # test with proportions and perfect overlap between
        # huc and basin
        testA = runoff.calculate_geometric_runoff(
            geom_id="A",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin'
            )
        # should return runoff from site 01
        assert testA['estimated_runoff'].tolist() == np.round(self.runoff_df[self.runoff_df['site_no'] == '01'].runoff, 5).tolist()  # noqa: E501
        # test with percentages rather than proportions
        testA_2 = runoff.calculate_geometric_runoff(
            geom_id="A",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection_perc,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='perc_basin_in_huc',
            prop_geom_in_basin_col='perc_huc_in_basin',
            percentage=True
            )
        # should return runoff from site 01
        assert testA_2['estimated_runoff'].tolist() == np.round(self.runoff_df[self.runoff_df['site_no'] == '01'].runoff, 5).tolist()  # noqa: E501

    def test_calculate_geometric_runoff_within_contains_huc(self):
        """Test runoff function with huc that has a basin containing
        it and a basin within it."""
        # huc contains basin and a basin contains huc
        testB = runoff.calculate_geometric_runoff(
            geom_id="B",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin'
            )

        check = self.runoff_df[self.runoff_df['site_no'].isin(['04', '05'])].reset_index()  # noqa: E501
        check = check.pivot(columns='site_no', index='datetime', values='runoff').dropna(axis='columns')  # noqa: E501
        int = self.geom_intersection.loc[self.geom_intersection['site_id'].isin(['04', '05'])]  # noqa: E501
        int['weight'] = int['prop_basin_in_huc'] * int['prop_huc_in_basin']
        weighted = np.round(np.average(check, weights=int['weight'], axis=1), 5)  # noqa: E501
        # should return weighted runoff from sites 04 and 05
        assert testB['estimated_runoff'].tolist() == weighted.tolist()

    def test_calculate_geometric_runoff_multiple_downstream_basins(self):
        """Test runoff function with huc that has two downstream basins"""
        # huc contained by two larger basins
        # test when more downstream basin clipped
        # from runoff calc
        testC = runoff.calculate_geometric_runoff(
            geom_id="C",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin',
            clip_downstream_basins=True
            )
        # should return site 07 runoff
        assert np.round(testC['estimated_runoff'].tolist(), decimals=5).tolist() == np.round(self.runoff_df[self.runoff_df['site_no'] == '07'].runoff, decimals=5).tolist()  # noqa: E501
        # huc contained by two larger basins
        # and overlaps another basin
        # test when all basins included
        # in weighted runoff calc
        testC_2 = runoff.calculate_geometric_runoff(
            geom_id="C",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin',
            clip_downstream_basins=False
            )

        check = self.runoff_df[self.runoff_df['site_no'].isin(['07', '08', '09'])].reset_index()  # noqa: E501
        check = check.pivot(columns='site_no', index='datetime', values='runoff').dropna(axis='columns')  # noqa: E501
        int = self.geom_intersection.loc[self.geom_intersection['site_id'].isin(['07', '08', '09'])]  # noqa: E501
        int['weight'] = int['prop_basin_in_huc'] * int['prop_huc_in_basin']
        weighted = np.round(np.average(check, weights=int['weight'], axis=1), 5)  # noqa: E501
        # should return weighted runoff from sites 07,08,09
        assert testC_2['estimated_runoff'].tolist() == weighted.tolist()

    def test_calculate_geometric_runoff_one_basin_in_huc(self):
        """Test runoff function with huc that contains a basin only"""
        # huc only contains a basin, not contained by
        # any basins
        testD = runoff.calculate_geometric_runoff(
            geom_id="D",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin',
            clip_downstream_basins=False
            )
        # should return runoff for site 010
        assert np.round(testD['estimated_runoff'].tolist(), decimals=5).tolist() == np.round(self.runoff_df[self.runoff_df['site_no'] == '010'].runoff, decimals=5).tolist()  # noqa: E501

    def test_calculate_geometric_runoff_no_basin_data(self):
        """Test runoff function with huc where no basin data
        exist."""
        # basin containing huc does not have data
        testE = runoff.calculate_geometric_runoff(
            geom_id="E",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin',
            clip_downstream_basins=False)
        assert testE.empty

    def test_calculate_geometric_runoff_nan_data_value(self):
        """Test runoff function with basin runoff with daily
        value that is nan."""
        testG = runoff.calculate_geometric_runoff(
            geom_id="G",
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin')
        # runoff value on last day should be runoff from basin '015'
        # since basin '014' is nan on that day
        assert np.round(testG.iloc[3]['estimated_runoff'], decimals=5) == np.round(self.runoff_df[self.runoff_df['site_no'] == '015'].runoff[3], decimals=5)  # noqa: E501

    def test_calculate_multiple_geometric_runoff(self):
        """Test multiple runoff function."""
        test_mult = runoff.calculate_multiple_geometric_runoff(
            geom_id_list=['A', 'B', 'C', 'D'],
            runoff_df=self.runoff_df,
            geom_intersection_df=self.geom_intersection,
            site_col='site_id',
            geom_id_col='huc_id',
            prop_basin_in_geom_col='prop_basin_in_huc',
            prop_geom_in_basin_col='prop_huc_in_basin')
        assert test_mult.shape == (16, 7)
        assert test_mult.index.name == 'datetime'
