import pandas as pd

calendar_Files = [
    "Raw_Data/calendar_12-2023.csv",
    "Raw_Data/calendar_06-2024.csv",
    "Raw_Data/calendar_03-2024.csv",
    "Raw_Data/calendar_09-2024.csv"
]

#Reading, importint and concatenating the csv files into a single dataframe
dataframes_calendar = [pd.read_csv(file, low_memory=False) for file in calendar_Files]
calendar_data = pd.concat(dataframes_calendar, ignore_index=True)

#DATA INSPECTION
print(calendar_data.info())
print(calendar_data.shape)

#CHECKING DUPLICATES 
duplicate_count = calendar_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# Display the duplicate rows
duplicates = calendar_data[calendar_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
review_data = calendar_data.drop_duplicates(keep="first")

# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(review_data)}")

#Changing data types 
# Remove dollar signs and commas, then convert to numeric type
calendar_data['price'] = pd.to_numeric(calendar_data['price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False))
calendar_data['adjusted_price'] = pd.to_numeric(calendar_data['adjusted_price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False))

#Changing date into datetime
calendar_data['date'] = pd.to_datetime(calendar_data['date'])

# Verify data types
print("\nData types:")
print(calendar_data.dtypes)

#CHECKING MISSING VALUES 
print(calendar_data.isna().sum())
# Filter dataset
filtered_data = calendar_data[calendar_data['adjusted_price'].notna()]

# Analyze the 'price' column for these rows
price_values = filtered_data[['price', "adjusted_price"]]

# Summary statistics
print(price_values.describe())
#Following analysis we can safely delete the adjusted price 
#The values are the same in the price column
calendar_data = calendar_data.drop(columns="adjusted_price")

#CHECKING Minimum/maximum night missing values 
print(calendar_data[["minimum_nights", "maximum_nights"]].isna().sum())

# Check for empty strings or unexpected placeholders
print(calendar_data[calendar_data['minimum_nights'] == ''])
print(calendar_data[calendar_data['maximum_nights'] == ''])

# Remove rows where 'nights' is missing
calendar_data_cleaned = calendar_data.dropna(subset=['minimum_nights', 'maximum_nights'])

# Calculate removed rows
removed_rows = len(calendar_data) - len(calendar_data_cleaned)
print(f"\nNumber of removed rows: {removed_rows}")

#LAST DATA VALIDATION
print(calendar_data_cleaned.info())
print(calendar_data_cleaned.shape)
print(calendar_data_cleaned.isna().sum())

#transforming the dataframe into csv 
calendar_data_cleaned.to_csv("calendar_data.csv", index=False)

