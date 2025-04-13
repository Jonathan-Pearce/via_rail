import os
import json

import pipeline.helpers as helpers  

# Path to the folder containing raw data files
raw_data_folder = 'raw_data'

#setup database connection
con, cur = helpers.connect_to_database("via_data.db")

# Iterate through each file in the folder
for filename in os.listdir(raw_data_folder):
    file_path = os.path.join(raw_data_folder, filename)
    
    # Check if it's a file and has a .json extension
    if os.path.isfile(file_path) and filename.endswith('.json'):
        print(f"Processing JSON file: {filename}")
        with open(file_path, 'r') as file:
            try:
                content = json.load(file)
                # Process the JSON content as needed
                helpers.json_data_to_database(content)
                #print(content)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {filename}: {e}")



