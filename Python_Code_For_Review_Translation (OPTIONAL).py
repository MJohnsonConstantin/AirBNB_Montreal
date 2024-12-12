
import os
import unicodedata
import pandas as pd
import numpy as np
import regex as re
import torch
import requests
from googletrans import Translator
import googletrans
from functools import lru_cache
import time  # Import time for adding delays

translator = Translator()
print(translator)
print(googletrans.__version__)  # Ensure it says '4.0.0-rc1'


review_Files = [
    "Raw_Data/reviews_12-2023.csv",
    "Raw_Data/reviews_06-2024.csv",
    "Raw_Data/reviews_03-2024.csv",
    "Raw_Data/reviews_09-2024.csv"
]

#Reading, important and concatenating the csv files into a single dataframe
dataframes_review = [pd.read_csv(file, low_memory=False) for file in review_Files]
review_data = pd.concat(dataframes_review, ignore_index=True)

#DATA VALIDATION 
print(review_data.info())

# Fill all missing values with the string "missing"
review_data.fillna("missing", inplace=True)

# Verify that there are no more missing values
print("Missing values after filling:")
print(review_data.isnull().sum())

# Remove rows where 'comments' is "missing"
review_data = review_data[review_data["comments"] != "missing"]

# Verify remaining data
print(f"Rows after removing missing comments: {len(review_data)}")

#Check the total number of duplicates
duplicate_count = review_data.duplicated().sum()
print(f"Total duplicate rows: {duplicate_count}")

# Display the duplicate rows
duplicates = review_data[review_data.duplicated()]
print("Duplicate rows:")
print(duplicates)

# Keep only the first occurrence
review_data = review_data.drop_duplicates(keep="first")
# Verify the result
print(f"Rows after keeping the first occurrence of duplicates: {len(review_data)}")

#Transofrming COLUMNS INTO THE RIGHT DATA TYPE
# Convert 'date' to datetime format
review_data["date"] = pd.to_datetime(review_data["date"], errors="coerce")

#validating the datatype transformation
print(review_data.info())

#TRANSFORMING THE REVIEW COLUMNS TEXT
def clean_text(comment):
    # Normalize text
    comment = unicodedata.normalize('NFKC', comment)

    # Remove HTML tags
    comment = re.sub(r"<.*?>", " ", comment)

    # Remove numbers
    comment = re.sub(r"\d+", "", comment)

    # Remove special characters (except French accents and punctuation)
    comment = re.sub(r"[^a-zA-Z0-9\s.,!?éèêàçùôöäëïûâ]", "", comment)

    # Convert to lowercase
    comment = comment.lower()

    # Remove extra spaces
    comment = re.sub(r"\s+", " ", comment).strip()

    return comment


# removing rows with less than 5 caracters 
review_data = review_data[review_data['comments'].str.len() > 10]
max_length = 2000
review_data = review_data[review_data['comments'].str.len() <= max_length]

# Apply to the comments column
review_data['comments_cleaned'] = review_data['comments'].apply(clean_text)
review_data["comments_cleaned"] = review_data["comments_cleaned"].astype("string")
review_data["comments"] = review_data["comments"].fillna("").astype("string")
print(review_data.dtypes)

# DATA TEXT VALIDATION 
print(review_data['comments_cleaned'].head(100))

special_chars = review_data['comments_cleaned'].str.contains(r"[^a-zA-Z0-9\s.,!?éèêàçùôöäëïûâ]", regex=True)
print(review_data[special_chars].head())

#TRY THE TRANSLATION ON THE SAMPLE DATA
sample_size = 10000
sampling_data = review_data[["comments_cleaned"]].head(sample_size)

# %% TRANSLATING WITH GOOGLE API (TRANLSATE AND REPHRASE)
@lru_cache(maxsize=10000)  # Cache up to 10,000 comments
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

#TEST for one row
paraphrased_comment = paraphrase_with_google_cached("how is you doing", intermediate_lang='fr')
print(paraphrased_comment)

comments = ["This is a test.", "buenos dias", "Yet another one."]
paraphrased_comments = paraphrase_with_google_batch_cached(comments, intermediate_lang='fr')
print(paraphrased_comments)

# Fixed parameters for processing
batch_size = 10  # Number of rows per batch
max_requests_before_pause = 180  # Pause after this many requests
delay_between_batches = 5 # Fixed delay between each batch (in seconds)
long_pause_duration = 60  # Pause duration after reaching max_requests_before_pause (in seconds)
retries = 1  # Number of retry attempts for failed batches
total_rows = len(sampling_data)  # Total number of rows in your data
checkpoint_file = "checkpoint.txt"  # To track the last completed batch
output_file = "processed_data.csv"  # To save the processed results

# Function to load the last checkpoint
def load_last_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            return int(f.read().strip())
    return 0  # Start from the first batch if no checkpoint exists

# Function to save the checkpoint
def save_checkpoint(batch_num):
    with open(checkpoint_file, "w") as f:
        f.write(str(batch_num))

# Load the last processed batch
start_batch = load_last_checkpoint()

# Track the total number of requests sent
total_requests_sent = 0

# Calculate the number of batches
num_batches = len(sampling_data) // batch_size + (1 if len(sampling_data) % batch_size != 0 else 0)

for i in range(num_batches):
    start = i * batch_size
    end = min((i + 1) * batch_size, len(sampling_data))
    print(f"Processing batch {i + 1}/{num_batches} (rows {start} to {end - 1})...")

    # Extract the current batch
    comments_batch = sampling_data['comments_cleaned'].iloc[start:end].tolist()

    # Flag to track batch success
    success = False
    paraphrased_batch = []

    try:
        # Retry loop for the batch
        for attempt in range(retries):
            try:
                paraphrased_batch = paraphrase_with_google_batch_cached(comments_batch, intermediate_lang='fr')
                if len(paraphrased_batch) == len(comments_batch):

                    success = True
                    break  # Exit retry loop if successful
                else:
                    print(f"Batch size mismatch in batch {i + 1}: "
                          f"Expected {len(comments_batch)}, got {len(paraphrased_batch)}. Retrying...")
            except Exception as e:
                print(f"Error in batch {i + 1}, attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    print("Retrying after 10 seconds...")
                    time.sleep(10)  # Retry delay
                else:
                    print(f"Max retries reached for batch {i + 1}. Skipping batch.")
        # Handle the batch if it succeeded or failed
        if success:
            # Assign translated results back to the DataFrame
            sampling_data.loc[start:end - 1, 'comments_paraphrased'] = paraphrased_batch
        else:
            # Log the skipped batch
            print(f"Skipping batch {i + 1}. Assigning None for all rows in this batch.")
            sampling_data.loc[start:end - 1, 'comments_paraphrased'] = [None] * len(comments_batch)

        # Track total requests sent and handle pauses
        total_requests_sent += len(comments_batch)
        if total_requests_sent >= max_requests_before_pause:
            print(f"Reached {max_requests_before_pause} requests. Pausing for {long_pause_duration} seconds...")
            time.sleep(long_pause_duration)
            total_requests_sent = 0  # Reset counter after pause
        else:
            time.sleep(delay_between_batches)  # Fixed delay between batches

    except Exception as fatal_error:
        # Handle any fatal error that would crash the loop
        print(f"Critical error in batch {i + 1}: {fatal_error}")
        print("Skipping this batch and continuing with the next...")

print("Processing complete!")
