import pandas as pd
import re

"""A utility script for cleaning and processing CSV files from social media data sources.

This script provides functions to clean text-based data, handling common issues like
newlines, non-ASCII characters, and large number representations (K, M).

Functions:
    Xcleaner: Processes a CSV file by removing unwanted characters and formatting.
    redditCleaner: Specializes in cleaning Reddit posts from JSON-like structures.

"""


def Xcleaner(input_file, output_file):
    """Process a CSV file to remove unwanted characters and format data properly.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path where cleaned data will be saved.

    Notes:
        The function processes specific columns by removing newlines, non-ASCII chars,
        and replacing 'K' or 'M' with zeros. It also drops duplicates before saving.

    Raises:
        Exception: If any required column values cannot be processed.
    """

    df = pd.read_csv(input_file, encoding="utf-8")

    # Loop over each item in the specified column (column 3)
    for i in range(len(df[df.columns[3]].values)):
        try:
            df.iloc[i, 3] = df.iloc[i, 3].replace("\n", "")
            df.iloc[i, 3] = re.sub(r"[^\x00-\x7F]+", "", df.iloc[i, 3])
            df.iloc[i, 4] = df.iloc[i, 4].replace("K", "000")
            df.iloc[i, 4] = df.iloc[i, 4].replace("M", "000000")
            df.iloc[i, 5] = df.iloc[i, 5].replace("K", "000")
            df.iloc[i, 5] = df.iloc[i, 5].replace("M", "000000")
            df.iloc[i, 6] = df.iloc[i, 6].replace("K", "000")
            df.iloc[i, 6] = df.iloc[i, 6].replace("M", "000000")

        except Exception as e:
            print(f"Error processing row {i}: {e}")

    # Save the cleaned DataFrame to a new CSV file
    df = df.drop_duplicates()
    df.to_csv(output_file, encoding="utf-8", index=False)

    # Print the column names
    print(df.columns.values)

    return
