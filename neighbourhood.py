# %%
import pandas as pd

neighbourhoods_Files = [
    "Raw_Data/neighbourhoods_12-2023.csv",
    "Raw_Data/neighbourhoods_06-2024.csv",
    "Raw_Data/neighbourhoods_03-2024.csv",
    "Raw_Data/neighbourhoods_09-2024.csv"
]

#Reading, important and concatenating the csv files into a single dataframe
dataframes_neighbourhoods = [pd.read_csv(file, low_memory=False) for file in neighbourhoods_Files]
neighbourhoods_data = pd.concat(dataframes_neighbourhoods, ignore_index=True)

#%% DATA VALIDATION 
print(neighbourhoods_data.info())
# %% DELETING NEIGH_GROUP 
neighbourhoods_data = neighbourhoods_data.drop(columns="neighbourhood_group")

# %% CHECKING DUPLICATES
# Check the total number of duplicates
duplicate_count = neighbourhoods_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# Display the duplicate rows
duplicates = neighbourhoods_data[neighbourhoods_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
neighbourhoods_data = neighbourhoods_data.drop_duplicates(keep="first")

# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(neighbourhoods_data)}")

# %% LAST DATA VALIDATION 
print(neighbourhoods_data.isna().sum())

# %% TRANSFORMING THE DATAFRAME INTO A CSV 
neighbourhoods_data.to_csv("neighbourhoods_data.csv", index=False)

# %%
