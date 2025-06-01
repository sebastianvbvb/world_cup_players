import os
import json
import pandas as pd

from pathlib import Path


# Starting from current working directory
current_path = Path.cwd()


# Target folder name
project_name = 'world_cup_players'

# Look for the project folder in the path
if project_name in current_path.parts:
    index = current_path.parts.index(project_name)
    project_root = Path(*current_path.parts[:index + 1])
    data_path = project_root / 'data' / 'raw' / 'json'
    output_path = project_root / 'data' / 'raw' / 'xlsx'

else:
    raise ValueError(f"'{project_name}' not found in path")
    
    
# Loop through all files in the folder
for filename in os.listdir(data_path):
    if filename.endswith('.json'):
        json_file_path = os.path.join(data_path, filename)

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])  # Make it a one-row dataframe
        else:
            print(f"Skipping {filename}: Unsupported JSON structure")
            continue
        
        if filename == 'countries.json':
            df = df.transpose().reset_index()
            df.columns = ['country', 'link']  # Optional: clean column names

        if filename == 'federations.json':
            df = df.transpose().reset_index()
            df.columns = ['country', 'federation']  # Optional: clean column names
        if filename == 'world_cups.json':
                df = df.transpose().reset_index()
                df.columns = ['cup', 'link']  # Optional: clean column names    
        excel_filename = os.path.splitext(filename)[0] + '.xlsx'
        excel_file_path = os.path.join(output_path, excel_filename)
        df.to_excel(excel_file_path, index=False)
        print(f"Converted {filename} to {excel_filename}")
