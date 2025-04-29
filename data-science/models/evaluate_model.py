import pandas as pd
import pickle
import os
import yaml
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# Load features and labels
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# Split into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Load trained model from file
model_path = os.path.join('models', 'purchase_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Load config to get best threshold
config_path = 'config/config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

best_threshold = config.get('best_threshold', 0.5)

# Predict probabilities on validation set
y_val_probs = model.predict_proba(X_val)[:, 1]

# Convert probabilities to binary predictions using threshold
y_val_pred = (y_val_probs >= best_threshold).astype(int)

# Evaluate metrics
accuracy = accuracy_score(y_val, y_val_pred)
precision = precision_score(y_val, y_val_pred)
recall = recall_score(y_val, y_val_pred)
f1 = f1_score(y_val, y_val_pred)

# Print evaluation results
print("\n✅ Model evaluation using best threshold:")
print(f"Best Threshold: {best_threshold:.4f}")
print(f"Accuracy     : {accuracy:.4f}")
print(f"Precision    : {precision:.4f}")
print(f"Recall       : {recall:.4f}")
print(f"F1 Score     : {f1:.4f}\n")