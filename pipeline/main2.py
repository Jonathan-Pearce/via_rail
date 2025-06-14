import os
import json
import pandas as pd

import helpers

# Path to the folder containing raw data files
clean_data_folder = 'clean_data'

#setup database connection
con, cur = helpers.connect_to_database("via_data.db")

# Iterate through each file in the folder
for filename in os.listdir(clean_data_folder):
    file_path = os.path.join(clean_data_folder, filename)
    
    # Check if it's a file and has a .json extension
    if os.path.isfile(file_path) and filename.endswith('.csv'):
        print(f"Processing CSV file: {filename}")
        with open(file_path, 'r') as file:
            content = pd.read_csv(file)
            # Process the CSV content as needed
            helpers.data_to_database(content, con, cur)



