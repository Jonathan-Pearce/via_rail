"""
Feature Engineering Script for Via Rail Data

This script performs feature engineering on the filtered Via Rail dataset:
1. Creates lagged features for diffMin grouped by train_id and instance
2. Converts 'from' and 'to' columns to one-hot encoded features
"""

import pandas as pd
import numpy as np


def load_data(filepath):
    """Load the filtered Via Rail data."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df


def create_lag_features(df, column='diffMin', group_cols=['train_id', 'instance'], lags=[1, 2, 3]):
    """
    Create lagged features for a specified column grouped by train_id and instance.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    column : str
        Column name to create lags for (default: 'diffMin')
    group_cols : list
        Columns to group by (default: ['train_id', 'instance'])
    lags : list
        List of lag values to create (default: [1, 2, 3])
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with added lag features
    """
    print(f"\nCreating lag features for '{column}' grouped by {group_cols}...")
    df = df.copy()
    
    # Sort by group columns and stop_id to ensure proper ordering
    df = df.sort_values(group_cols + ['stop_id']).reset_index(drop=True)
    
    # Create lagged features
    for lag in lags:
        lag_col_name = f'{column}_lag_{lag}'
        df[lag_col_name] = df.groupby(group_cols)[column].shift(lag)
        print(f"  Created {lag_col_name}")
    
    return df


def create_onehot_features(df, columns=['from', 'to']):
    """
    Convert categorical columns to one-hot encoded features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    columns : list
        List of column names to one-hot encode (default: ['from', 'to'])
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with one-hot encoded features
    """
    print(f"\nCreating one-hot encoded features for columns: {columns}...")
    df = df.copy()
    
    for col in columns:
        if col in df.columns:
            # Get unique values
            unique_values = sorted(df[col].unique())
            print(f"  Column '{col}' has {len(unique_values)} unique values")
            
            # Create one-hot encoded columns
            onehot_df = pd.get_dummies(df[col], prefix=col, prefix_sep='_')
            
            # Add to original dataframe
            df = pd.concat([df, onehot_df], axis=1)
            print(f"  Created {len(onehot_df.columns)} one-hot columns for '{col}'")
        else:
            print(f"  Warning: Column '{col}' not found in dataframe")
    
    return df


def calculate_time_to_stop(df, time_col='scheduled', lag_col='scheduled_lag_1'):
    """
    Calculate time to next stop in minutes using scheduled time and its lag.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    time_col : str
        Column name with scheduled time (default: 'scheduled')
    lag_col : str
        Column name with lagged scheduled time (default: 'scheduled_lag_1')
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with added time_to_stop_minutes feature
    """
    print(f"\nCalculating time_to_stop_minutes from '{time_col}' and '{lag_col}'...")
    df = df.copy()
    
    # Convert to datetime if not already
    if df[time_col].dtype == 'object':
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    
    if lag_col in df.columns and df[lag_col].dtype == 'object':
        df[lag_col] = pd.to_datetime(df[lag_col], errors='coerce')
    
    # Calculate time difference in minutes
    if lag_col in df.columns:
        df['time_to_stop_minutes'] = (df[time_col] - df[lag_col]).dt.total_seconds() / 60.0
        print(f"  Created time_to_stop_minutes")
        print(f"  Min: {df['time_to_stop_minutes'].min():.2f} minutes")
        print(f"  Max: {df['time_to_stop_minutes'].max():.2f} minutes")
        print(f"  Mean: {df['time_to_stop_minutes'].mean():.2f} minutes")
    else:
        print(f"  Warning: Column '{lag_col}' not found, cannot calculate time_to_stop_minutes")
    
    return df


def save_engineered_data(df, output_path):
    """Save the feature-engineered dataset."""
    print(f"\nSaving feature-engineered data to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"Successfully saved {len(df)} rows with {len(df.columns)} columns")


def main():
    """Main function to execute feature engineering pipeline."""
    # Configuration
    input_file = 'via_data_filtered.csv'
    output_file = 'via_data_feature_engineered.csv'
    
    # Load data
    df = load_data(input_file)
    
    # Display initial data info
    print("\n" + "="*60)
    print("INITIAL DATA INFO")
    print("="*60)
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    # Create lag features for diffMin
    print("\n" + "="*60)
    print("CREATING LAG FEATURES FOR DIFFMIN")
    print("="*60)
    df = create_lag_features(df, column='diffMin', group_cols=['train_id', 'instance'], lags=[1, 2, 3])
    
    # Create lag features for scheduled
    print("\n" + "="*60)
    print("CREATING LAG FEATURES FOR SCHEDULED")
    print("="*60)
    df = create_lag_features(df, column='scheduled', group_cols=['train_id', 'instance'], lags=[1])
    
    # Calculate time to stop in minutes
    print("\n" + "="*60)
    print("CALCULATING TIME TO STOP")
    print("="*60)
    df = calculate_time_to_stop(df, time_col='scheduled', lag_col='scheduled_lag_1')
    
    # Create one-hot encoded features
    print("\n" + "="*60)
    print("CREATING ONE-HOT ENCODED FEATURES")
    print("="*60)
    df = create_onehot_features(df, columns=['from', 'to'])
    
    # Display final data info
    print("\n" + "="*60)
    print("FINAL DATA INFO")
    print("="*60)
    print(f"Shape: {df.shape}")
    print(f"Total columns: {len(df.columns)}")
    print(f"\nNew columns added:")
    new_cols = [col for col in df.columns if col not in load_data(input_file).columns]
    for col in new_cols:
        print(f"  - {col}")
    
    # Display sample of engineered features
    print(f"\nSample of lag features:")
    lag_cols = [col for col in df.columns if 'lag' in col]
    display_cols = ['train_id', 'instance', 'stop_id', 'diffMin']
    if 'time_to_stop_minutes' in df.columns:
        display_cols.append('time_to_stop_minutes')
    if lag_cols:
        # Show first 3 lag columns to avoid clutter
        print(df[display_cols + lag_cols[:3]].head(10))
    
    # Save the engineered dataset
    save_engineered_data(df, output_file)
    
    print("\n" + "="*60)
    print("FEATURE ENGINEERING COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
