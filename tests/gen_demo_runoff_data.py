"""Code to generate runoff data for the unit tests."""
import numpy as np
import pandas as pd

# set the seed
np.random.seed(42)

# making the test fraction of drainage area per state
# columns are 2-letter state abbreviations
# rows are fractions of areas
# sum across rows is 1
df_frac_da = pd.DataFrame({
    "07108900": np.random.random(4).tolist(),
    "07103980": np.random.random(4).tolist(),
    "01646500": np.random.random(4).tolist(),
}, index=["AL", "NY", "MN", "WI"]).T
# set one value to 0
df_frac_da.iloc[0, 0] = 0
# loop down rows and normalize
for i in range(3):
    df_frac_da.iloc[i, :] = \
        df_frac_da.iloc[i, :] / np.sum(df_frac_da.iloc[i, :])
# assert that the sum of each row is 1
assert np.allclose(np.sum(df_frac_da, axis=1), np.ones(3))

# make test fraction of state per drainage area
df_frac_state = pd.DataFrame({
    "AL": np.random.random(3).tolist(),
    "NY": np.random.random(3).tolist(),
    "MN": np.random.random(3).tolist(),
    "WI": np.random.random(3).tolist()
}, index=["07108900", "07103980", "01646500"])
# set one value to 0
df_frac_state.iloc[2, 1] = 0
# loop across columns and normalize
for i in range(4):
    df_frac_state.iloc[:, i] = \
        df_frac_state.iloc[:, i] / np.sum(df_frac_state.iloc[:, i])
# assert that the sum of each column is 1
assert np.allclose(np.sum(df_frac_state, axis=0), np.ones(4))

# make the weights table by doing element-wise multiplication
df_weights = df_frac_da * df_frac_state.values
# save the dataframe
df_weights.to_json("demo_weights.json")
