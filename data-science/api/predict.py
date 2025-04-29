import pickle
import yaml
import os
import pandas as pd
import psycopg2

# Load model and preprocessing artifacts
with open(os.path.join(os.path.dirname(__file__), '..', 'models', 'purchase_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(os.path.dirname(__file__), '..', 'models', 'feature_list.pkl'), 'rb') as f:
    feature_list = pickle.load(f)

with open(os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)

# Preprocess input data (convert ID to name, one-hot encode, scale numerics)
def preprocess_input(data):
    # Connect to PostgreSQL and fetch mapping names from ID
    conn = psycopg2.connect(
        host="localhost", port=5435,
        dbname="data-learning", user="admin", password="admin123"
    )

    # Convert IDs to actual names
    gender = pd.read_sql("SELECT name FROM genders WHERE id = %s", conn, params=[data['gender_id']]).iloc[0, 0]
    occupation = pd.read_sql("SELECT name FROM occupations WHERE id = %s", conn, params=[data['occupation_id']]).iloc[0, 0]
    location = pd.read_sql("SELECT name FROM locations WHERE id = %s", conn, params=[data['location_id']]).iloc[0, 0]
    product_type = pd.read_sql("SELECT name FROM products WHERE id = %s", conn, params=[data['product_type_id']]).iloc[0, 0]
    conn.close()

    # Construct one-row input DataFrame
    df = pd.DataFrame([{
        'age': data['age'],
        'gender': gender,
        'annual_income': data['annual_income'],
        'occupation': occupation,
        'location': location,
        'family_assets': data['family_assets'],
        'product_type': product_type
    }])

    # Add derived features
    df['age_level'] = df['age'].apply(lambda x: 1 if x < 18 else 0)
    df['asset_level'] = df['family_assets'].apply(lambda x: 1 if x < 200000 else 0)

    # One-hot encode categorical features
    df = pd.get_dummies(df, columns=['gender', 'occupation', 'location', 'product_type'])

    # Scale numeric features using the fitted scaler
    numerical_features = ['age', 'annual_income', 'family_assets']
    df[numerical_features] = scaler.transform(df[numerical_features])

    # Add missing columns if necessary to match training feature list
    for col in feature_list:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns to match model input
    df = df[feature_list]

    return df.values

# Prediction entry point
def predict_purchase(data):
    # Re-read threshold from config each time
    with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml'), 'r') as f:
        config = yaml.safe_load(f)
    threshold = config.get('best_threshold', 0.5)
    input_array = preprocess_input(data)
    proba = model.predict_proba(input_array)[0][1]
    prediction = int(proba >= threshold)
    return {
        "Purchased": prediction,
        "Probability": round(float(proba), 4)
    }