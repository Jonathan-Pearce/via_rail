"""
Machine Learning Regression Model for Predicting diffMin

This script trains a regression model to predict diffMin (delay in minutes)
using cross-validation for robust evaluation.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_validate, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


def load_data(filepath):
    """Load the feature-engineered Via Rail data."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df


def prepare_features(df, target='diffMin', exclude_cols=None):
    """
    Prepare features for modeling.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target : str
        Target variable name
    exclude_cols : list
        List of columns to exclude from features
    
    Returns:
    --------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        Target variable
    feature_names : list
        List of feature names
    """
    print("\n" + "="*60)
    print("PREPARING FEATURES")
    print("="*60)
    
    df = df.copy()
    
    # Default columns to exclude
    if exclude_cols is None:
        exclude_cols = []
    
    # Always exclude these columns
    always_exclude = [
        target,  # Target variable
        'diff',  # Explicitly excluded as per requirement
        'train_id',  # Identifier
        'instance',  # Identifier (date)
        'stop_id',  # Sequential identifier
        'station',  # Station name (redundant with code)
        'code',  # Station code (already in from/to one-hot)
        'estimated',  # Timestamp
        'scheduled',  # Timestamp
        'eta',  # Status category
    ]
    
    exclude_cols = list(set(always_exclude + exclude_cols))
    
    # Separate features and target
    available_exclude = [col for col in exclude_cols if col in df.columns]
    X = df.drop(columns=available_exclude, errors='ignore')
    y = df[target].copy()
    
    # Convert boolean columns to integers
    bool_cols = X.select_dtypes(include=['bool']).columns
    if len(bool_cols) > 0:
        print(f"\nConverting {len(bool_cols)} boolean columns to integers")
        X[bool_cols] = X[bool_cols].astype(int)
    
    # Handle any remaining non-numeric columns
    non_numeric = X.select_dtypes(exclude=['number']).columns.tolist()
    if non_numeric:
        print(f"\nDropping non-numeric columns: {non_numeric}")
        X = X.drop(columns=non_numeric)
    
    # Remove rows with missing target values
    valid_idx = ~y.isna()
    X = X[valid_idx].reset_index(drop=True)
    y = y[valid_idx].reset_index(drop=True)
    
    print(f"\nFeature matrix shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Features included: {X.columns.tolist()[:10]}..." if len(X.columns) > 10 else f"Features included: {X.columns.tolist()}")
    print(f"\nTarget statistics:")
    print(f"  Mean: {y.mean():.2f}")
    print(f"  Std: {y.std():.2f}")
    print(f"  Min: {y.min():.2f}")
    print(f"  Max: {y.max():.2f}")
    
    return X, y, X.columns.tolist()


def train_with_cross_validation(X, y, model=None, cv_folds=5, random_state=42):
    """
    Train model with cross-validation.
    
    Parameters:
    -----------
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        Target variable
    model : sklearn estimator
        Model to train (default: RandomForestRegressor)
    cv_folds : int
        Number of cross-validation folds
    random_state : int
        Random seed for reproducibility
    
    Returns:
    --------
    model : trained model
    cv_results : dict
        Cross-validation results
    """
    print("\n" + "="*60)
    print("TRAINING MODEL WITH CROSS-VALIDATION")
    print("="*60)
    
    # Default model
    if model is None:
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=random_state,
            n_jobs=-1
        )
    
    print(f"\nModel: {type(model).__name__}")
    print(f"Cross-validation folds: {cv_folds}")
    
    # Handle missing values
    X_clean = X.fillna(X.mean())
    
    # Setup cross-validation
    kfold = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    # Scoring metrics
    scoring = {
        'neg_mse': 'neg_mean_squared_error',
        'neg_mae': 'neg_mean_absolute_error',
        'r2': 'r2'
    }
    
    print("\nPerforming cross-validation...")
    cv_results = cross_validate(
        model, 
        X_clean, 
        y, 
        cv=kfold, 
        scoring=scoring,
        return_train_score=True,
        n_jobs=-1
    )
    
    # Calculate metrics
    train_rmse = np.sqrt(-cv_results['train_neg_mse'])
    test_rmse = np.sqrt(-cv_results['test_neg_mse'])
    train_mae = -cv_results['train_neg_mae']
    test_mae = -cv_results['test_neg_mae']
    train_r2 = cv_results['train_r2']
    test_r2 = cv_results['test_r2']
    
    print("\n" + "="*60)
    print("CROSS-VALIDATION RESULTS")
    print("="*60)
    print(f"\nTraining Metrics (mean ± std across {cv_folds} folds):")
    print(f"  RMSE: {train_rmse.mean():.4f} ± {train_rmse.std():.4f}")
    print(f"  MAE:  {train_mae.mean():.4f} ± {train_mae.std():.4f}")
    print(f"  R²:   {train_r2.mean():.4f} ± {train_r2.std():.4f}")
    
    print(f"\nValidation Metrics (mean ± std across {cv_folds} folds):")
    print(f"  RMSE: {test_rmse.mean():.4f} ± {test_rmse.std():.4f}")
    print(f"  MAE:  {test_mae.mean():.4f} ± {test_mae.std():.4f}")
    print(f"  R²:   {test_r2.mean():.4f} ± {test_r2.std():.4f}")
    
    # Train final model on all data
    print("\nTraining final model on full dataset...")
    model.fit(X_clean, y)
    
    # Feature importance (if available)
    if hasattr(model, 'feature_importances_'):
        print("\n" + "="*60)
        print("TOP 10 MOST IMPORTANT FEATURES")
        print("="*60)
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
    
    return model, cv_results


def evaluate_model(model, X, y):
    """
    Evaluate trained model on the full dataset.
    
    Parameters:
    -----------
    model : trained sklearn model
        Trained model
    X : pd.DataFrame
        Feature matrix
    y : pd.Series
        True target values
    """
    print("\n" + "="*60)
    print("FINAL MODEL EVALUATION ON FULL DATA")
    print("="*60)
    
    X_clean = X.fillna(X.mean())
    y_pred = model.predict(X_clean)
    
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    print(f"\nMetrics on full dataset:")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  R²:   {r2:.4f}")
    
    # Prediction examples
    print("\n" + "="*60)
    print("SAMPLE PREDICTIONS")
    print("="*60)
    results_df = pd.DataFrame({
        'Actual': y[:10].values,
        'Predicted': y_pred[:10],
        'Error': y[:10].values - y_pred[:10]
    })
    print(results_df.to_string(index=False))


def main():
    """Main function to execute ML pipeline."""
    # Configuration
    input_file = 'via_data_feature_engineered.csv'
    
    # Load data
    df = load_data(input_file)
    
    # Prepare features
    X, y, feature_names = prepare_features(df, target='diffMin', exclude_cols=['diff'])
    
    # Train model with cross-validation
    model, cv_results = train_with_cross_validation(
        X, 
        y, 
        model=None,  # Use default RandomForestRegressor
        cv_folds=5,
        random_state=42
    )
    
    # Evaluate on full dataset
    evaluate_model(model, X, y)
    
    print("\n" + "="*60)
    print("MODEL TRAINING COMPLETE!")
    print("="*60)
    print("\nModel is ready for predictions.")
    print(f"Number of features used: {len(feature_names)}")


if __name__ == "__main__":
    main()
