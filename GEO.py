# %%
import pandas as pd
import geopandas as gpd


GEO_Files = [
    "Raw_Data/neighbourhoods_GEO_12-2023.geojson",
    "Raw_Data/neighbourhoods_GEO_06-2024.geojson",
    "Raw_Data/neighbourhoods_GEO_03-2024.geojson",
    "Raw_Data/neighbourhoods_GEO_09-2024.geojson"
]

#Reading, important and concatenating the csv files into a single dataframe
dataframes_GEO = [gpd.read_file(file) for file in GEO_Files]
GEO_data = gpd.GeoDataFrame(pd.concat(dataframes_GEO,  ignore_index=True))

#%% DATA VALIDATION 
print(GEO_data.info())
print(GEO_data["neighbourhood_group"])

# %% DELETING neigh_group columns
GEO_data = GEO_data.drop(columns="neighbourhood_group")

# %% CHECKING DUPLICATES
# Check the total number of duplicates
duplicate_count = GEO_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# Display the duplicate rows
duplicates = GEO_data[GEO_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
GEO_data = GEO_data.drop_duplicates(keep="first")

# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(GEO_data)}")

# %% LAST DATA VALIDATION 
print(GEO_data.isna().sum())

# %% TRANSFORMING THE DATAFRAME INTO A CSV 
GEO_data.to_csv("GEO_data.csv", index=False)
