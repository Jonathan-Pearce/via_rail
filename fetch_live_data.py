"""
Fetch Live VIA Rail Tracking Data

This script pulls live tracking data from VIA Rail's API and filters for
trains that are currently running (have latitude and longitude values).
"""

import requests
import pandas as pd
import json
from datetime import datetime


def fetch_via_rail_data(url='https://tsimobile.viarail.ca/data/allData.json'):
    """
    Fetch live data from VIA Rail API.
    
    Parameters:
    -----------
    url : str
        API endpoint URL
    
    Returns:
    --------
    dict
        JSON response from API
    """
    print(f"Fetching data from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched data")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def extract_running_trains(data):
    """
    Extract trains that are currently running (have lat, lng values).
    
    Parameters:
    -----------
    data : dict
        Raw JSON data from API
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with running trains
    """
    print("\nExtracting running trains...")
    
    if not data:
        print("No data to process")
        return pd.DataFrame()
    
    running_trains = []
    
    # Parse the data structure
    # The API typically returns trains in a nested structure
    for key, value in data.items():
        if isinstance(value, dict):
            # Check if this is a train with location data
            if 'lat' in value and 'lng' in value:
                lat = value.get('lat')
                lng = value.get('lng')
                
                # Only include trains with valid lat/lng
                if lat is not None and lng is not None and lat != '' and lng != '':
                    train_info = {
                        'train_id': key,
                        'lat': lat,
                        'lng': lng,
                    }
                    
                    # Add all other available fields
                    for field, val in value.items():
                        if field not in ['lat', 'lng']:
                            train_info[field] = val
                    
                    running_trains.append(train_info)
        elif isinstance(value, list):
            # Handle case where data is a list of trains
            for train in value:
                if isinstance(train, dict) and 'lat' in train and 'lng' in train:
                    lat = train.get('lat')
                    lng = train.get('lng')
                    
                    if lat is not None and lng is not None and lat != '' and lng != '':
                        train_info = train.copy()
                        running_trains.append(train_info)
    
    df = pd.DataFrame(running_trains)
    
    if len(df) > 0:
        print(f"Found {len(df)} trains currently running")
        print(f"Columns: {df.columns.tolist()}")
    else:
        print("No running trains found")
    
    return df


def display_train_summary(df):
    """
    Display summary of running trains.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with running trains
    """
    if len(df) == 0:
        print("\nNo trains to display")
        return
    
    print("\n" + "="*60)
    print("RUNNING TRAINS SUMMARY")
    print("="*60)
    print(f"\nTotal trains currently running: {len(df)}")
    
    # Display first few trains
    print(f"\nFirst few running trains:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df.head(10))
    
    # Display column info
    print(f"\n" + "="*60)
    print("DATA STRUCTURE")
    print("="*60)
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nData types:")
    print(df.dtypes)


def save_live_data(df, output_file='via_live_data.csv'):
    """
    Save live data to CSV file.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with running trains
    output_file : str
        Output file path
    """
    if len(df) == 0:
        print("\nNo data to save")
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file_timestamped = output_file.replace('.csv', f'_{timestamp}.csv')
    
    print(f"\nSaving data to {output_file_timestamped}...")
    df.to_csv(output_file_timestamped, index=False)
    print(f"Successfully saved {len(df)} trains")
    
    # Also save without timestamp for easy access
    df.to_csv(output_file, index=False)
    print(f"Also saved to {output_file} (overwritten)")


def main():
    """Main function to fetch and process live VIA Rail data."""
    print("="*60)
    print("VIA RAIL LIVE TRACKING DATA FETCHER")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Fetch data from API
    data = fetch_via_rail_data()
    
    if data:
        # Save raw JSON for reference
        print("\nSaving raw JSON data...")
        with open('via_live_data_raw.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Saved to via_live_data_raw.json")
        
        # Extract running trains
        df = extract_running_trains(data)
        
        # Display summary
        display_train_summary(df)
        
        # Save to CSV
        if len(df) > 0:
            save_live_data(df)
        
        print("\n" + "="*60)
        print("FETCH COMPLETE!")
        print("="*60)
    else:
        print("\nFailed to fetch data from API")


if __name__ == "__main__":
    main()
