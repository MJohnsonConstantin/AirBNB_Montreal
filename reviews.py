
# %%
import os
import unicodedata
import pandas as pd
import numpy as np
import regex as re
import torch
import requests
from googletrans import Translator
import time  # For delays
translator = Translator()
API_URL = "http://localhost:5000/translate"

review_Files = [
    "Raw_Data/reviews_12-2023.csv",
    "Raw_Data/reviews_06-2024.csv",
    "Raw_Data/reviews_03-2024.csv",
    "Raw_Data/reviews_09-2024.csv"
]


#Reading, important and concatenating the csv files into a single dataframe
dataframes_review = [pd.read_csv(file, low_memory=False) for file in review_Files]
review_data = pd.concat(dataframes_review, ignore_index=True)

#%% DATA VALIDATION 
print(review_data.info())
# %% FILL MISSING_VALUE WITH "MISSING"
# Fill all missing values with the string "missing"
review_data.fillna("missing", inplace=True)

# Verify that there are no more missing values
print("Missing values after filling:")
print(review_data.isnull().sum())

# Remove rows where 'comments' is "missing"
review_data = review_data[review_data["comments"] != "missing"]

# Verify remaining data
print(f"Rows after removing missing comments: {len(review_data)}")

# %% CHECKING FOR DUPLICATES 
# Check the total number of duplicates
duplicate_count = review_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# 50 rows max
pd.set_option("display.max_rows", 50)  # Show all rows
# Display the duplicate rows
duplicates = review_data[review_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
review_data = review_data.drop_duplicates(keep="first")
# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(review_data)}")

# %% Transofrming COLUMNS INTO THE RIGHT DATA TYPE
# Convert 'date' to datetime format
review_data["date"] = pd.to_datetime(review_data["date"], errors="coerce")

#validating the datatype transformation
print(review_data.info())

# %% TRANSFORMING THE REVIEW COLUMNS TEXT
def clean_text(comment):
    # Normalize text
    comment = unicodedata.normalize('NFKC', comment)
    
    # Remove HTML tags
    comment = re.sub(r"<.*?>", " ", comment)
    
    # Remove numbers
    comment = re.sub(r"\d+", "", comment)
    
    # Replace exclamation marks with dots
    comment = comment.replace("!", ".")
    
    # Remove special characters (except French accents and punctuation)
    comment = re.sub(r"[^a-zA-Z0-9\s.,!?èéàçùôöâäêëîïüû]", "", comment)
    
    # Convert to lowercase
    comment = comment.lower()
    
    # Remove extra spaces
    comment = re.sub(r"\s+", " ", comment).strip()
    
    return comment


# removing rows with less than 5 caracters 
review_data = review_data[review_data['comments'].str.len() > 10]
max_length = 2000
review_data = review_data[review_data['comments'].str.len() <= max_length]


#%%
# Apply to the comments column
review_data['comments_cleaned'] = review_data['comments'].apply(clean_text)
review_data["comments_cleaned"] = review_data["comments_cleaned"].astype("string")
review_data["comments"] = review_data["comments"].fillna("").astype("string")
print(review_data.dtypes)


# %% DATA TEXT VALIDATION 
print(review_data['comments_cleaned'].head(100))


#%%
special_chars = review_data['comments_cleaned'].str.contains(r"[^a-zA-Z0-9\s.,!?éèêàçùôöäëïûâ]", regex=True)
print(review_data[special_chars].head())

# %%
sample_size = 1000
sampling_data = review_data[['id', 'comments_cleaned']].head(sample_size)

# %%

# Fixed parameters for processing
batch_size = 10  # Number of rows per batch
max_requests_before_pause = 180  # Pause after this many requests
delay_between_batches = 6  # Fixed delay between each batch (in seconds)
long_pause_duration = 60  # Pause duration after reaching max_requests_before_pause (in seconds)
retries = 2  # Number of retry attempts for failed batches

# Files for tracking progress and saving processed data
checkpoint_file = "checkpoint.txt"
output_file = "processed_data.csv"


# Function to load the last checkpoint
def load_last_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            content = f.read().strip()
            if content:  # Check if content is not empty
                return int(content)
            else:
                return 0  # Return 0 if the file is empty
    return 0  # Start from the first batch if no checkpoint exists

# Function to save the checkpoint
def save_checkpoint(batch_num):
    with open(checkpoint_file, "w") as f:
        f.write(str(batch_num))
    print(f"Checkpoint saved: Batch {batch_num}")

# Function to save a processed batch to the output file
def save_batch_to_file(batch_data, is_first_batch=False):
    if is_first_batch:
        batch_data.to_csv(output_file, index=False, mode="w")  # Write with headers
    else:
        batch_data.to_csv(output_file, index=False, mode="a", header=False)  # Append without headers
    print(f"Batch saved to '{output_file}'")

# Simulated paraphrasing function (replace with your real paraphrasing logic)
def paraphrase_with_google_cached(comment, intermediate_lang='fr'):
    """
    Paraphrase a single comment using round-trip translation with caching.
    """
    try:
        # Step 1: Translate to the intermediate language
        intermediate = translator.translate(comment, src='auto', dest=intermediate_lang).text

        # Step 2: Translate back to English
        paraphrased = translator.translate(intermediate, src=intermediate_lang, dest='en').text

        return paraphrased
    except Exception as e:
        print(f"Error paraphrasing comment: {comment} -> {e}")
        return comment  # Return the original comment on error
    

    # Translating a batch of comments with caching
def paraphrase_with_google_batch_cached(comments_batch, intermediate_lang='fr'):
    """
    Paraphrase a batch of comments using round-trip translation with caching.
    """
    paraphrased = []
    for comment in comments_batch:
        try:
            paraphrased.append(paraphrase_with_google_cached(comment, intermediate_lang))
        except Exception as e:
            print(f"Error paraphrasing comment in batch: {comment} -> {e}")
            paraphrased.append(comment)  # Return original comment on error
    return paraphrased

# %%
# Load the last processed batch
start_batch = load_last_checkpoint()
is_first_batch = start_batch == 0  # If it's the first batch, we need to write headers

# Track the total number of requests sent
total_requests_sent = 0

last_saved_index = 0
# Calculate the number of batches
num_batches = len(sampling_data) // batch_size + (1 if len(sampling_data) % batch_size != 0 else 0)

for i in range(start_batch, num_batches):
    try:
        start = i * batch_size
        end = min((i + 1) * batch_size, len(sampling_data))
        print(f"Processing batch {i + 1}/{num_batches} (rows {start} to {end - 1})...")

        comments_batch = sampling_data['comments_cleaned'].iloc[start:end].tolist()

        success = False
        paraphrased_batch = []

        # Retry logic for the batch
        for attempt in range(retries):
            try:
                paraphrased_batch = paraphrase_with_google_batch_cached(
                    comments_batch, intermediate_lang='fr'
                )
                if len(paraphrased_batch) == len(comments_batch):
                    success = True
                    break
            except Exception as e:
                print(f"Error in batch {i + 1}, attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(10)  # Retry delay
                else:
                    print("Max retries reached. Skipping this batch.")

        # Handle the results
        if success:
            sampling_data.loc[start:end - 1, 'comments_paraphrased'] = paraphrased_batch
        else:
            print(f"Skipping batch {i + 1}. Assigning None for all rows in this batch.")
            sampling_data.loc[start:end - 1, 'comments_paraphrased'] = None


        # Handle pauses for API limits
        total_requests_sent += len(comments_batch)
        if total_requests_sent >= max_requests_before_pause:
            print(f"Reached {max_requests_before_pause} requests. Pausing for {long_pause_duration} seconds...")
            new_rows = sampling_data.iloc[last_saved_index:end]
            save_batch_to_file(new_rows, append=True)  # Append the new rows to the file
            # Save the checkpoint
            save_checkpoint(i + 1)
            # Update the last saved index
            last_saved_index = end
            time.sleep(long_pause_duration)
            total_requests_sent = 0  # Reset counter after pause
        else:
            time.sleep(delay_between_batches)  # Delay between batches

    except Exception as e:
        print(f"Critical error in batch {i + 1}: {e}. Skipping this batch and continuing.")
        # Optionally, log the error or take additional actions for skipped batches.

print("Processing complete!")



# %%