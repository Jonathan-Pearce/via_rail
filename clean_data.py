import json
import pandas as pd
import os
from pathlib import Path

def json_to_dataframe(json_file_path, output_csv_path=None):
    """
    Convert Via Rail JSON data to a tabular DataFrame.
    
    Args:
        json_file_path: Path to the JSON file
        output_csv_path: Optional path to save CSV (if None, will auto-generate)
    
    Returns:
        DataFrame with the converted data
    """
    
    # Read JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # List to store all rows
    rows = []
    
    # Loop through all train IDs
    for train_id, train_info in data.items():
        # Extract train-level information
        train_departed = train_info.get('departed', None)
        train_arrived = train_info.get('arrived', None)
        train_from = train_info.get('from', None)
        train_to = train_info.get('to', None)
        train_instance = train_info.get('instance', None)
        
        # Loop through all stops in times array
        times = train_info.get('times', [])
        for i, stop in enumerate(times):
            # Create row with train info and stop info
            row = {
                'train_id': train_id,
                'departed': train_departed,
                'arrived': train_arrived,
                'from': train_from,
                'to': train_to,
                'instance': train_instance,
                'stop_id': i,  # Using index as stop ID since not explicitly provided
                'station': stop.get('station', None),
                'code': stop.get('code', None),
                'estimated': stop.get('estimated', None),
                'scheduled': stop.get('scheduled', None),
                'eta': stop.get('eta', None),
                'diff': stop.get('diff', None),
                'diffMin': stop.get('diffMin', None)
            }
            rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Generate output CSV path if not provided
    if output_csv_path is None:
        input_file = Path(json_file_path)
        output_csv_path = input_file.parent / f"{input_file.stem}_converted.csv"
    
    # Save to CSV
    df.to_csv(output_csv_path, index=False)
    print(f"Data saved to: {output_csv_path}")
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def process_raw_data_folder(raw_data_dir, output_dir=None):
    """
    Process all JSON files in raw_data folder, selecting one file per day.
    Selects the file with timestamp closest to and before 4am for each day.
    
    Args:
        raw_data_dir: Path to the raw_data directory
        output_dir: Directory to save converted CSV files (if None, uses parent dir)
    
    Returns:
        List of tuples (date, input_file, output_file)
    """
    from datetime import datetime, time
    from glob import glob
    
    # Get all JSON files in raw_data directory
    json_files = glob(os.path.join(raw_data_dir, "*.json"))
    print(f"Found {len(json_files)} JSON files in {raw_data_dir}")
    
    # Parse filenames and group by date
    files_by_date = {}
    
    for filepath in json_files:
        filename = os.path.basename(filepath)
        
        # Parse filename: Via_data_2025-04-02 03:59:40.621979.json
        if filename.startswith("Via_data_"):
            try:
                # Extract datetime string (between "Via_data_" and ".json")
                datetime_str = filename[9:-5]  # Remove "Via_data_" prefix and ".json" suffix
                
                # Parse datetime
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
                date_key = dt.date()
                
                # Only consider files before 4am (04:00:00)
                if dt.time() < time(4, 0, 0):
                    if date_key not in files_by_date:
                        files_by_date[date_key] = []
                    files_by_date[date_key].append((dt, filepath))
            except Exception as e:
                print(f"Warning: Could not parse filename {filename}: {e}")
    
    # Select the file closest to 4am for each date
    selected_files = {}
    for date_key, file_list in files_by_date.items():
        # Sort by datetime and select the last one (closest to 4am)
        file_list.sort(key=lambda x: x[0])
        selected_dt, selected_path = file_list[-1]
        selected_files[date_key] = (selected_dt, selected_path)
    
    print(f"\nSelected {len(selected_files)} files (one per day):")
    for date_key in sorted(selected_files.keys()):
        dt, filepath = selected_files[date_key]
        print(f"  {date_key}: {os.path.basename(filepath)} ({dt.strftime('%H:%M:%S')})")
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.dirname(raw_data_dir)
    
    # Process each selected file
    processed_files = []
    print("\nProcessing files...")
    
    for date_key in sorted(selected_files.keys()):
        dt, json_file = selected_files[date_key]
        
        # Generate output filename
        output_filename = f"Via_data_{date_key}_converted.csv"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"\nProcessing {os.path.basename(json_file)}...")
        try:
            df = json_to_dataframe(json_file, output_path)
            processed_files.append((date_key, json_file, output_path))
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Pipeline complete! Processed {len(processed_files)} files.")
    print(f"Output directory: {output_dir}")
    
    return processed_files


# Example usage for your specific file
if __name__ == "__main__":
    # Option 1: Process single file
    # json_file = "/workspaces/via_rail/raw_data/Via_data_2025-04-02 03:59:40.621979.json"
    # output_file = "/workspaces/via_rail/Via_data_2025-04-02_converted.csv"
    # df = json_to_dataframe(json_file, output_file)
    
    # Option 2: Process entire raw_data folder (one file per day)
    raw_data_dir = "/workspaces/via_rail/raw_data"
    output_dir = "/workspaces/via_rail/clean_data"
    
    processed_files = process_raw_data_folder(raw_data_dir, output_dir)
    
    # Display summary
    print(f"\nProcessed files:")
    for date_key, input_file, output_file in processed_files:
        print(f"  {date_key}: {os.path.basename(output_file)}")