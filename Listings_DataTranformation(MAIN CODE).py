# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

#Listing the file directory
listing_Files = [
    "Raw_Data/listings_12-2023.csv",
    "Raw_Data/listings_06-2024.csv",
    "Raw_Data/listings_03-2024.csv",
    "Raw_Data/listings_09-2024.csv"
]
#Reading, important and concatenating the csv files into a single dataframe
dataframes_listing = [pd.read_csv(file, low_memory=False) for file in listing_Files]
listing_data = pd.concat(dataframes_listing, ignore_index=True)

# %% #DATA VALIDATION - Exploring the DataFrame
print(listing_data.info())

# %% #DUPLICATE ANALYSES + transforming date into quarter
# Check for duplicate rows
duplicates = listing_data[listing_data.duplicated()]
print("Number of duplicate rows:", duplicates.shape[0])

# %% Separating the data in quarters
# Data exploration
print(listing_data["last_scraped"].value_counts())
print(listing_data["last_scraped"].isna().sum())
print(listing_data["last_scraped"].dtype)

# Transform last_scraped into datetime
listing_data["last_scraped"] = pd.to_datetime(listing_data["last_scraped"], errors="coerce")
print(listing_data["last_scraped"].dtype)

# Function to assign quarter based on timestamp
def assign_quarter(date):
    if date == pd.Timestamp("2023-12-13"):
        return "Q1"
    elif date == pd.Timestamp("2024-03-23"):
        return "Q2"
    elif date in [pd.Timestamp("2024-06-18"), pd.Timestamp("2024-06-19")]:
        return "Q3"
    elif date == pd.Timestamp("2024-09-13"):
        return "Q4"
    else:
        return "Unknown"  # For unexpected dates

# Apply the function to the last_scraped column
listing_data["quarter"] = listing_data["last_scraped"].apply(assign_quarter)
print(listing_data["quarter"].value_counts())

#DELETING THE LAST SCRAPED COLUMN
listing_data = listing_data.drop(columns="last_scraped")


# %% #LISTING COLUMNS DELETION
listing_deleted_columns = [   #10 columns deleted
    "description", "neighborhood_overview", 
    "host_url", "picture_url", "host_picture_url", 
    "neighbourhood", "neighbourhood_group_cleansed", 
    "bathrooms", "price", "calendar_updated"]

listing_data = listing_data.drop(columns=listing_deleted_columns)

# %% #Handeling the bathrooms_text columns missing values 
# Function to Extract the number of bathrooms
def extract_bathrooms_number(text):
    if pd.isna(text):  # Handle NaN values
        return None
    if "Half" in text or "half" in text:
        # Check if there's a number before "Half" and add 0.5
        parts = text.split()
        try:
            number = float(parts[0]) if parts[0].replace('.', '', 1).isdigit() else 0
            return number + 0.5
        except ValueError:
            return 0.5
    else:
        # Extract numeric part from the string
        try:
            return float(text.split()[0])
        except ValueError:
            return None

# Function to Extract the type of bathroom (remove the number)
def extract_bathroom_type(text):
    if pd.isna(text):  # Handle NaN values
        return None
    parts = text.split()
    return " ".join(parts[1:]) if len(parts) > 1 else None

# Apply the functions to create new columns
listing_data["bathroom_number"] = listing_data["bathrooms_text"].apply(extract_bathrooms_number)
listing_data["bathroom_type"] = listing_data["bathrooms_text"].apply(extract_bathroom_type)

#Mapping to transform the remaining data label  
bathroom_type_mapping = {
    "bath": "bath",
    "baths": "bath",
    "half-bath": "bath",  # Include half-bath in the "bath" category
    "shared bath": "shared bath",
    "shared baths": "shared bath",
    "private bath": "private bath"
}
# Apply the mapping to the bathroom_type column
listing_data["bathroom_type"] = listing_data["bathroom_type"].replace(bathroom_type_mapping)

# Display the grouped counts
print(listing_data["bathroom_type"].value_counts())
print("Missing Values in bathroom_number:", listing_data["bathroom_number"].isnull().sum())
print("Missing Values in bathroom_type:", listing_data["bathroom_type"].isnull().sum())

# DATA IMPUTATION AFTER TRANSFORMING THE BATHROOM COLUMS
# Fill missing values in bathroom_number with 1
listing_data["bathroom_number"] = listing_data["bathroom_number"].fillna(1)

# Fill missing values in bathroom_type with 'bath'
listing_data["bathroom_type"] = listing_data["bathroom_type"].fillna("bath")

# Verify there are no missing values left
print("Missing Values in bathroom_number:", listing_data["bathroom_number"].isnull().sum())
print("Missing Values in bathroom_type:", listing_data["bathroom_type"].isnull().sum())

#DELETING BATHROOMS_TEXT
listing_data = listing_data.drop(columns=["bathrooms_text"])
# %%  #HOST_LOCATION
print(listing_data["host_location"].value_counts())
print("Number of missing host_location DATA :")
print(listing_data["host_location"].isna().sum())
#Since the variable doesn't look to be insightful, let's remove it
listing_data = listing_data.drop(columns="host_location")

# %% HOST_IS_SUPEROST
#DATA EXPLORATION
print(listing_data["host_is_superhost"].value_counts())
print("number of missing value for super_host:")
print(listing_data["host_is_superhost"].isna().sum())

# Separate the groups to explorer potentiel relationship for missingness
missing_superhost = listing_data[listing_data["host_is_superhost"].isnull()]
non_missing_superhost = listing_data[listing_data["host_is_superhost"].notnull()]

# Summary statistics for missing superhost values
print("Summary for missing superhost values:")
print(missing_superhost["number_of_reviews"].describe())

# Summary statistics for non-missing superhost values
print("\nSummary for non-missing superhost values:")
print(non_missing_superhost["number_of_reviews"].describe())

# Add a column to label missing vs non-missing
listing_data["superhost_status"] = listing_data["host_is_superhost"].fillna("missing")

# Plot the boxplot
plt.figure(figsize=(8, 6))
sns.boxplot(x="superhost_status", y="number_of_reviews", data=listing_data)
plt.title("Comparison of Number of Reviews by Superhost Status")
plt.xlabel("Superhost Status")
plt.ylabel("Number of Reviews")
plt.show()

# Plot histograms for each group
plt.figure(figsize=(10, 6))
sns.histplot(missing_superhost["number_of_reviews"], label="Missing Superhost", color="red", kde=True)
sns.histplot(non_missing_superhost["number_of_reviews"], label="Non-Missing Superhost", color="blue", kde=True)
plt.title("Distribution of Number of Reviews")
plt.xlabel("Number of Reviews")
plt.ylabel("Frequency")
plt.legend()
plt.show()

#PERSONAL NOTE 
#The majority of host_is_superhost values are f (22,846 out of 34,964 non-missing).
#No strong evidence that missing values are more likely to be superhosts, 

#it's safer to assume they are not superhosts.
listing_data["host_is_superhost"] = listing_data["host_is_superhost"].fillna("f")
# Delete the create superhost_status
listing_data = listing_data.drop(columns="superhost_status")

# %% HOST_ABOUT -- Boolean transformation
print("Number of missing host_about DATA :")
print(listing_data["host_about"].isna().sum())

#About half of the data is missing. I will transform the data into a boolean, with True having a description
listing_data["has_host_description"] = listing_data["host_about"].notnull()
print(listing_data["has_host_description"].value_counts())

#DELETE THE HOST_ABOUT
listing_data = listing_data.drop(columns="host_about")


# %% CALCULATING HOST_TENURE
#transform host_since in datetime
listing_data["host_since"] = pd.to_datetime(listing_data["host_since"], errors="coerce")
print(listing_data["host_since"].dtype)

# Calculate host tenure in days
listing_data["host_tenure"] = (
    datetime.now() - listing_data["host_since"]
).dt.days.fillna(0)  # Replace with 0 or another default value

# %% #EXPLORING MISSINGNESS IN host_data (time, rate, acceptance)
#Transforming host_reponse_rate and host_acceptance_rate 
listing_data["host_response_rate"] = (
    listing_data["host_response_rate"]
    .str.replace("%", "", regex=False)  # Remove the percentage symbol
    .astype(float)  # Convert to float
)
# Convert host_acceptance_rate to numeric
listing_data["host_acceptance_rate"] = (
    listing_data["host_acceptance_rate"]
    .str.replace("%", "", regex=False)  # Remove the percentage symbol
    .astype(float)  # Convert to float
)

#missing values in all 3 columns
missing_all_three = listing_data[
    listing_data["host_response_time"].isnull() &
    listing_data["host_response_rate"].isnull() &
    listing_data["host_acceptance_rate"].isnull()
]

#non-missing values
non_missing_all_three = listing_data[
    ~(
        listing_data["host_response_time"].isnull() &
        listing_data["host_response_rate"].isnull() &
        listing_data["host_acceptance_rate"].isnull()
    )
]

# Create a DataFrame of missingness indicators for (time and rate)
missingness = listing_data[["host_response_time", "host_response_rate"]].isnull()

# Check for correlations between missingness
missing_corr = missingness.corr()
print(missing_corr)
# All missing values in response time are also missing value in response rate

# Compare tenure on missing vs non missing values in (time,rate, acceptance)
print("TENURE Data for missing values :")
print(missing_all_three.shape)
print(missing_all_three["host_tenure"].describe())
print("TENURE Data for non-missing values")
print(non_missing_all_three.shape)
print(non_missing_all_three["host_tenure"].describe())


# Compare numbers of reviews in the last 12 month of missing vs non missing values 
print(missing_all_three["number_of_reviews_ltm"].describe())
print(non_missing_all_three["number_of_reviews_ltm"].describe())

#PERSONAL NOTE
#Missing rows are likely associated with inactive or less popular listings, which explains the low review counts.
#Host Engagement:Hosts with missing response data might be less engaged with the platform, possibly because they are inactive, legacy, or part-time hosts.
#The comparaison indicates that the missing value have way lower numbers of review, more than 
#half ot the non-missing. Indicating that they might be new users

# %% (Rate, time) Data visualization to see the relationship between missingness and TENURE
#Step to analyse new users 
plt.figure(figsize=(10, 6))
plt.hist(missing_all_three["host_tenure"].dropna(), bins=20, alpha=0.5, label="Missing All Three")
plt.hist(non_missing_all_three["host_tenure"].dropna(), bins=20, alpha=0.5, label="Non-Missing")
plt.legend()
plt.title("Distribution of Host Since Dates")
plt.xlabel("host_tenure")
plt.ylabel("Count")
plt.show()

# Create a new column to mark missing vs non-missing
listing_data["missing_all_three"] = (
    listing_data["host_response_time"].isnull() &
    listing_data["host_response_rate"].isnull() &
    listing_data["host_acceptance_rate"].isnull()
)

sns.boxplot(
    x="missing_all_three",
    y="host_tenure",
    data=listing_data
)
plt.title("Host Tenure by Missing Status")
plt.xlabel("Missing All Three (True/False)")
plt.ylabel("Host Tenure")
plt.show()
#PERONAL NOTE : Data is not linked to new or inexperienced host
#Older hosts (joined earlier) are more likely to have missing values in all three columns.
#Newer hosts (post-2018) are less likely to have missing data.

# %% (Rate, time) FILTERING DATABASE TO ACCOUNT FOR MISSING VALUES IN (rate, time, acceptance)

#FILTERING THE DATASET TO REMOVE ROWS WHERE ALL 3 columns are missing and number of reviews is less than 3 (Removes inactive host)
listing_data_inactive = listing_data[listing_data['missing_all_three']]
listing_data = listing_data[~listing_data['missing_all_three']]

#VERIFYING THE REMAINING MISSING VALUE 
print(listing_data.shape)
print(listing_data[["host_acceptance_rate", "host_response_time", "host_response_rate"]].isna().sum())
print(listing_data["host_acceptance_rate"].describe())
print(listing_data["host_response_time"].value_counts())
print(listing_data["host_response_rate"].value_counts())

# %% (Rate, time) MEDIAN IMPUTATION FOR VALUES IN (Rate, time, acceptance)
listing_data["host_response_rate"] = listing_data["host_response_rate"].fillna(
    listing_data["host_response_rate"].median()
)
listing_data["host_acceptance_rate"] = listing_data["host_acceptance_rate"].fillna(
    listing_data["host_acceptance_rate"].median()
)
listing_data["host_response_time"] = listing_data["host_response_time"].fillna("within an hour")  

#Last verification to check mon missing value and if the imputation was done correctly 
print(listing_data[["host_acceptance_rate", "host_response_time", "host_response_rate"]].isna().sum())
print(listing_data["host_response_rate"].describe())
print(listing_data["host_acceptance_rate"].describe())
print(listing_data["host_response_time"].describe())

#DELETE THE CREATED MISSING ALL THREE COLUMNS
listing_data = listing_data.drop(columns="missing_all_three")

# %% BED and bedrooms columns ANALYSIS
missing_both = listing_data[listing_data["beds"].isnull() & listing_data["bedrooms"].isnull()]
print(missing_both.shape)
print(listing_data[["beds", "bedrooms"]].isna().sum())
print(listing_data["beds"].describe())
print(listing_data["bedrooms"].describe())
print(listing_data[["beds", "bedrooms"]].corr())

#PLOT TO UNDERSTAND THE RELATIONSHIP BERWEEN BEDS AND BEDROOMS
sns.scatterplot(x="bedrooms", y="beds", data=listing_data)
plt.title("Relationship Between Bedrooms and Beds")
plt.xlabel("Number of Bedrooms")
plt.ylabel("Number of Beds")
plt.show()

# %%(Beds & Bedroom)IMPUTATION BY THE AVERAGE BED PER BEDROOM
# Calculate the ratio of beds to bedrooms (exclude rows with missing values)
bed_to_bedroom_ratio = listing_data.loc[
    listing_data["beds"].notnull() & listing_data["bedrooms"].notnull(),
    "beds"
].mean() / listing_data.loc[
    listing_data["beds"].notnull() & listing_data["bedrooms"].notnull(),
    "bedrooms"
].mean()

# Impute missing beds based on bedrooms
listing_data.loc[listing_data["beds"].isnull(), "beds"] = (
    listing_data["bedrooms"] * bed_to_bedroom_ratio
)
# Impute missing bedrooms based on beds
listing_data.loc[listing_data["bedrooms"].isnull(), "bedrooms"] = (
    listing_data["beds"] / bed_to_bedroom_ratio)


#Impute rows where both missing bedrooms and bed with median 
median_beds = listing_data["beds"].median()
median_bedrooms = listing_data["bedrooms"].median()
listing_data.loc[
    listing_data["beds"].isnull() & listing_data["bedrooms"].isnull(), ["beds", "bedrooms"]
] = [median_beds, median_bedrooms]

print(listing_data[["beds", "bedrooms"]].isna().sum())
# %% has availability

print(listing_data['has_availability'].isna().sum())
print(listing_data['has_availability'].value_counts())

data_missing_availability = listing_data[listing_data["has_availability"].isna()]
data_true_availability = listing_data[listing_data["has_availability"] == "t"]
print(data_missing_availability["number_of_reviews_l30d"].describe())
print(data_true_availability["number_of_reviews_l30d"].describe())

#Lots of availability 0 -- probably inactive -- imput missing with false has availability
listing_data['has_availability'] = listing_data['has_availability'].fillna("f")

# %% host_neighborhood
print(listing_data["host_neighbourhood"].isna().sum())
listing_data = listing_data.drop(columns="host_neighbourhood")
## TOO MUCH MISSING VALUE WE DELETE THE COLUMS

# %% (REVIEW SCORES) #Analyse missing values for the reviews columns
# Subset the DataFrame to the desired columns
listing_review_columns = [
    "first_review", "last_review",
      "review_scores_rating", "review_scores_accuracy", "review_scores_checkin", 
      "review_scores_communication", "review_scores_location", "review_scores_value", "reviews_per_month" 
]
subset_data = listing_data[listing_review_columns]

# Calculate missing values and percentages for the subset
missing_values = subset_data.isnull().sum()
missing_percentage = (missing_values / len(subset_data)) * 100

# Combine into a DataFrame
missing_data_summary = pd.DataFrame({
    'Missing Values': missing_values,
    'Percentage (%)': missing_percentage
}).sort_values(by='Missing Values', ascending=False)

# Display the summary
print("Missing Values Summary for Selected Columns:")
print(missing_data_summary)

# %% Summary statistics for the Numeric Columns in the reviews 
# Check the data types of columns
print(listing_data[listing_review_columns].dtypes)

listing_review_columns.remove("first_review")
listing_review_columns.remove("last_review")
listing_review_columns.remove("reviews_per_month")

# Subset numeric columns from the selected columns
numeric_subset = subset_data.select_dtypes(include=['number'])

# Summary statistics for numeric columns in the subset
summary_stats = numeric_subset.describe().transpose()

# Add the median column
summary_stats['Median'] = numeric_subset.median()

# Display the summary statistics
print("\nSummary Statistics for Selected Numeric Columns:")
print(summary_stats)

# Plot histograms for numeric columns in the subset
for col in numeric_subset.columns:
    plt.figure()
    numeric_subset[col].hist(bins=20, edgecolor='black')
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.show()

# %% ANALYZING FREQUENCY AND MEAN FOR REVIEW SCORES 
mean_scores = listing_data[listing_review_columns].mean()
print(mean_scores)


for col in listing_review_columns:
    print(f"Frequency distribution for {col}:")
    print(listing_data[col].value_counts())
    print("\n")

#Boxplot visualization with rating depending on the review score
melted_data = listing_data[listing_review_columns].melt(var_name="Aspect", value_name="Rating")
plt.figure(figsize=(10, 6))
sns.boxplot(x="Aspect", y="Rating", data=melted_data)
plt.title("Distribution of Ratings Across Different Aspects")
plt.xlabel("Aspect")
plt.ylabel("Rating")
plt.xticks(rotation=45)
plt.show()    

#Correlation matrix between review scores 
correlation_matrix = listing_data[listing_review_columns].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Correlation Between Review Scores")
plt.show()
# %% Looking if missing data in review is associated with missing value in number of review 
#Check rows where all review columns are missing
missing_scores = listing_data[listing_review_columns].isnull().all(axis=1)

# Check where the number of reviews is 0 or missing
no_reviews = listing_data["number_of_reviews"].isnull() | (listing_data["number_of_reviews"] == 0)

# Identify inactive listings
listing_data["inactive_listing"] = missing_scores & no_reviews

#Finding the number of rows with no reviews score and no reviews 
inactive_count = listing_data["inactive_listing"].sum()
print(f"Number of inactive listings: {inactive_count}")

listing_data["inactive_listing"] = (missing_scores & no_reviews)
print(listing_data["inactive_listing"].value_counts())
# %% KEEPIGN INACTIVE LISTING IN A SEPARATE DATAFRAME (I want to join the data in filtered)
listing_data_active = listing_data[~listing_data["inactive_listing"]]
inactive_listings = listing_data[listing_data["inactive_listing"]]

# Concatenate inactive_listings and listing_data_inactive
all_inactive_listings = pd.concat([inactive_listings, listing_data_inactive], ignore_index=True)


#%% Check missing values for active listings 
missing_active = listing_data_active.isnull().sum()
missing_active = missing_active[missing_active > 0]  # Only show columns with missing values
print("Missing values in active listings:")
print(missing_active)

# %% CHECK IF THE REMAINING
# Identify rows with missing values in each column
missing_first_review = listing_data_active["first_review"].isnull()
missing_last_review = listing_data_active["last_review"].isnull()
missing_reviews_per_month = listing_data_active["reviews_per_month"].isnull()

# Check if the rows with missing 'first_review' and 'last_review' are the same as those missing 'reviews_per_month'
all_same = (missing_first_review & missing_last_review & missing_reviews_per_month).all()

if all_same:
    print("All rows with missing 'first_review' and 'last_review' also have 'reviews_per_month' missing.")
else:
    print("Not all rows with missing 'first_review' and 'last_review' have 'reviews_per_month' missing.")

# Display rows where all three columns are missing
all_three_missing = listing_data_active[
    missing_first_review & missing_last_review & missing_reviews_per_month
]
print("\nRows where 'first_review', 'last_review', and 'reviews_per_month' are all missing:")
print(all_three_missing)


# %%# Select the missing rows from listing_data_active
missing_rows_condition = (
    listing_data_active["first_review"].isnull() &
    listing_data_active["last_review"].isnull() &
    listing_data_active["reviews_per_month"].isnull()
)

rows_to_move = listing_data_active[missing_rows_condition]

# Add these rows to the inactive_listings DataFrame
all_inactive_listings = pd.concat([all_inactive_listings, rows_to_move], ignore_index=True)

# Remove these rows from listing_data_active
listing_data_active = listing_data_active[~missing_rows_condition]
print(f"Rows moved to inactive_listings: {len(rows_to_move)}")
print(f"Remaining rows in listing_data_active: {len(listing_data_active)}")

# %% IMPUTING THE REMAINING MISSING VALUE IN REVIEW BY THE MEDIAN 
# Define the review score columns that need imputation
review_score_cols = [
    "review_scores_accuracy", "review_scores_cleanliness", 
    "review_scores_checkin", "review_scores_communication", 
    "review_scores_location", "review_scores_value"
]

# Impute missing values in each column with the column's median
for col in review_score_cols:
    median_value = listing_data_active[col].median()  # Calculate median
    listing_data_active[col] = listing_data_active[col].fillna(median_value)  # Impute missing values

# Verify that missing values have been imputed
print("Missing values after imputation:")
print(listing_data_active[review_score_cols].isnull().sum())
# %% LAST DATA VALIDATION 
def verify_data(df, name):
    print(f"--- Verifying {name} ---")
    print(f"Shape: {df.shape}")  # Rows and columns
    print("\nMissing Values (if any):")
    print(df.isnull().sum())  # Count of missing values in each column
    print("\nDuplicate Rows:")
    print(df.duplicated().sum())  # Count duplicate rows
    print("\nSample Data:")
    print(df.head())  # Display the first 5 rows
    print("-" * 40)
#Set to see all rows
pd.set_option("display.max_rows", None)  # Show all rows
# Perform verification on listing_data_active
verify_data(listing_data_active, "Active Listings")    

# Check for overlaps between active and inactive data
print("\n--- Checking Overlap Between Active and Inactive Listings ---")
overlap = pd.merge(listing_data_active, all_inactive_listings, how="inner")
print(f"Number of overlapping rows: {len(overlap)}")
if not overlap.empty:
    print("Overlap Sample:")
    print(overlap.head())


# %% Tranforming the dataframe inactive and actice into a csv (ANALYSIS IN POWERBI IS ONLY WITH ACTIVE LISTINGS)
all_inactive_listings.to_csv("all_inactive_listings.csv", index=False)
listing_data_active.to_csv("listing_data_actice.csv", index=False)
