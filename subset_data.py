import pandas as pd

def subset_data(input_file, output_file):
    """
    Subset the dataset by excluding rows with train_id containing brackets '(' or ')'.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to save the filtered CSV file
    
    Returns:
        Filtered DataFrame
    """
    
    # Load the data
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    
    print(f"Original dataset shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"Unique trains: {df['train_id'].nunique():,}")
    
    # Filter out rows where train_id contains '(' or ')'
    df_filtered = df[~df['train_id'].str.contains(r'[()]', regex=True, na=False)]
    
    print(f"\nFiltered dataset shape: {df_filtered.shape[0]:,} rows × {df_filtered.shape[1]} columns")
    print(f"Unique trains: {df_filtered['train_id'].nunique():,}")
    print(f"Rows removed: {df.shape[0] - df_filtered.shape[0]:,}")
    
    # Save the filtered data
    df_filtered.to_csv(output_file, index=False)
    print(f"\nFiltered data saved to: {output_file}")
    
    return df_filtered


if __name__ == "__main__":
    input_file = "/workspaces/via_rail/via_data_aggregated.csv"
    output_file = "/workspaces/via_rail/via_data_filtered.csv"
    
    df_filtered = subset_data(input_file, output_file)
    
    print("\nSample of filtered train IDs:")
    print(df_filtered['train_id'].unique()[:10])
