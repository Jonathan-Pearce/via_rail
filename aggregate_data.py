import pandas as pd
import os
from glob import glob

def aggregate_clean_data(clean_data_dir, output_file=None):
    """
    Aggregate all CSV files in the clean_data folder into a single DataFrame.
    
    Args:
        clean_data_dir: Path to the clean_data directory
        output_file: Path to save the aggregated CSV (if None, auto-generate)
    
    Returns:
        Aggregated DataFrame
    """
    
    # Get all CSV files in clean_data directory
    csv_files = glob(os.path.join(clean_data_dir, "*.csv"))
    csv_files.sort()  # Sort for consistent ordering
    
    print(f"Found {len(csv_files)} CSV files in {clean_data_dir}")
    
    if len(csv_files) == 0:
        print("No CSV files found to aggregate.")
        return None
    
    # Read and concatenate all CSV files
    dfs = []
    for csv_file in csv_files:
        filename = os.path.basename(csv_file)
        print(f"Reading {filename}...")
        try:
            df = pd.read_csv(csv_file)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    # Concatenate all dataframes
    if len(dfs) == 0:
        print("No data to aggregate.")
        return None
    
    print(f"\nConcatenating {len(dfs)} dataframes...")
    aggregated_df = pd.concat(dfs, ignore_index=True)
    
    # Generate output filename if not provided
    if output_file is None:
        parent_dir = os.path.dirname(clean_data_dir)
        output_file = os.path.join(parent_dir, "via_data_aggregated.csv")
    
    # Save aggregated data
    aggregated_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"Aggregation complete!")
    print(f"Data saved to: {output_file}")
    print(f"Total rows: {len(aggregated_df):,}")
    print(f"Total columns: {len(aggregated_df.columns)}")
    print(f"Date range: {aggregated_df['instance'].min()} to {aggregated_df['instance'].max()}")
    print(f"Unique trains: {aggregated_df['train_id'].nunique()}")
    print(f"Unique stations: {aggregated_df['station'].nunique()}")
    
    return aggregated_df


if __name__ == "__main__":
    clean_data_dir = "/workspaces/via_rail/clean_data"
    output_file = "/workspaces/via_rail/via_data_aggregated.csv"
    
    # Aggregate all clean data
    df = aggregate_clean_data(clean_data_dir, output_file)
    
    if df is not None:
        print(f"\nFirst 5 rows:")
        print(df.head())
        print(f"\nData types:")
        print(df.dtypes)
