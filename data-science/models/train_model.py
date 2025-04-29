import pandas as pd
import pickle
import os
import lightgbm as lgb
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

# Create output directory for models
os.makedirs('models', exist_ok=True)

# Load features and labels
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# One-hot encode categorical features
X = pd.get_dummies(X, columns=['gender', 'occupation', 'location', 'product_type'])

# Standardize numerical columns
numerical_features = ['age', 'annual_income', 'family_assets']
scaler = StandardScaler()
X[numerical_features] = scaler.fit_transform(X[numerical_features])

# Save the fitted scaler for later use in inference
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Define LightGBM hyperparameter search space
param_grid = {
    'num_leaves': [15, 31],
    'max_depth': [-1, 10, 20],
    'learning_rate': [0.05, 0.1]
}

# Initialize LightGBM classifier
lgbm = lgb.LGBMClassifier(random_state=42, is_unbalance=True)

# Run grid search with cross-validation
grid_search = GridSearchCV(
    estimator=lgbm,
    param_grid=param_grid,
    cv=3,
    scoring='f1',
    n_jobs=-1,
    verbose=1
)

# Fit the model
grid_search.fit(X, y.values.ravel())

# Save the best model
with open('models/purchase_model.pkl', 'wb') as f:
    pickle.dump(grid_search.best_estimator_, f)

# Save the feature column order for inference alignment
with open('models/feature_list.pkl', 'wb') as f:
    pickle.dump(list(X.columns), f)

print("✅ Model training complete. Model and feature list have been saved.")