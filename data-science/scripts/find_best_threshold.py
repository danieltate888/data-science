import pandas as pd
import pickle
import os
import numpy as np
from sklearn.metrics import precision_recall_curve, f1_score
from sklearn.model_selection import train_test_split
import yaml

# Load preprocessed features and labels
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# One-hot encode categorical features (same as training step)
X = pd.get_dummies(X, columns=['gender', 'occupation', 'location', 'product_type'])

# Split into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Load the trained model
model_path = os.path.join('models', 'purchase_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Predict probabilities for the positive class (class 1)
y_val_probs = model.predict_proba(X_val)[:, 1]

# Compute precision, recall, and thresholds for validation set
precisions, recalls, thresholds = precision_recall_curve(y_val, y_val_probs)

# Compute F1 scores
f1s = 2 * (precisions * recalls) / (precisions + recalls)

# Find the threshold that gives the best F1 score
best_idx = np.argmax(f1s)
best_threshold = thresholds[best_idx]

# Output the best threshold and corresponding metrics
print("\n✅ Best threshold automatically identified:")
print(f"Best Threshold              : {best_threshold:.4f}")
print(f"Precision at best threshold: {precisions[best_idx]:.4f}")
print(f"Recall at best threshold   : {recalls[best_idx]:.4f}")
print(f"F1 Score at best threshold : {f1s[best_idx]:.4f}\n")

# Path to config file
config_path = 'config/config.yaml'

# Load existing configuration
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Update threshold value in config
config['best_threshold'] = float(best_threshold)

# Write updated config back to file
with open(config_path, 'w') as f:
    yaml.dump(config, f)

print(f"✅ Best threshold ({best_threshold:.4f}) has been written to config/config.yaml")