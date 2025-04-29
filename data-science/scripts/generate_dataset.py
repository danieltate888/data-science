import pandas as pd
import numpy as np
import random
import os

# Output path
save_path = 'data/raw/dataset.csv'

# Basic ID value pools
occupations = list(range(10))         # Occupation IDs: 0–9
product_types = list(range(10))       # Product type IDs: 0–9
locations = list(range(8))            # Location IDs: 0–7

# Define big vs small cities
big_cities = [0, 1, 2]                # Sydney, Melbourne, Brisbane
small_cities = [3, 4, 5, 6, 7]

# Product popularity weights (lower for cosmetics/bags/shoes)
product_hotness = {
    0: 0.9, 1: 0.9, 2: 0.8, 3: 0.6, 4: 0.7,
    5: 0.6, 6: 0.8, 7: 0.5, 8: 0.7, 9: 0.6
}

# Occupation-based influence on likelihood to purchase
occupation_influence = {
    0: 0.8, 1: 0.7, 2: 0.9, 3: 0.6, 4: 0.6,
    5: 0.7, 6: 0.85, 7: 0.65, 8: 0.5, 9: 0.85
}

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate 5000 synthetic user samples
samples = []
for _ in range(5000):
    Age = np.random.randint(0, 81)
    GenderID = np.random.randint(0, 2)
    AnnualIncome = np.random.randint(10000, 250001)
    OccupationID = random.choice(occupations)
    ProductTypeID = random.choice(product_types)
    LocationID = random.choice(locations)

    # Estimate family assets (income × multiplier + noise)
    asset_multiplier = np.random.uniform(5, 20)
    FamilyAssets = int(AnnualIncome * asset_multiplier + np.random.normal(0, 50000))
    FamilyAssets = max(10000, FamilyAssets)  # Ensure non-negative assets

    # Start score baseline
    score = 50

    # Age effect
    if Age < 18:
        score -= 70
    elif Age <= 30:
        score += 10
    elif Age <= 50:
        score += 5
    elif Age <= 65:
        score -= 5
    else:
        score -= 20

    # Income effect
    if AnnualIncome < 40000:
        score -= 25
    elif AnnualIncome > 120000:
        score += 20

    # Asset effect
    if FamilyAssets < 100000:
        score -= 30
    elif FamilyAssets > 1000000:
        score += 25

    # Gender-product preference bias
    if GenderID == 0 and ProductTypeID in [0, 1, 2, 6, 8]:
        score += 15
    if GenderID == 1 and ProductTypeID in [3, 4, 5, 7, 9]:
        score += 15

    # Big city bonus
    if LocationID in big_cities:
        score += 5
    else:
        score -= 5

    # Add product hotness effect
    score += (product_hotness.get(ProductTypeID, 0.6) - 0.6) * 20

    # Add occupation influence effect
    score += (occupation_influence.get(OccupationID, 0.7) - 0.7) * 20

    # Add Gaussian noise to simulate real-world behavior
    score += np.random.normal(0, 10)

    # Convert score to probability using sigmoid
    prob = 1 / (1 + np.exp(-0.12 * (score - 50)))
    prob = np.clip(prob, 0.01, 0.99)

    # Sample purchase outcome (1 or 0)
    Purchased = np.random.binomial(1, prob)

    # Append record
    samples.append([
        Age, GenderID, AnnualIncome, OccupationID, ProductTypeID, LocationID, FamilyAssets, Purchased
    ])

# Convert to DataFrame
df = pd.DataFrame(samples, columns=[
    'Age', 'GenderID', 'AnnualIncome', 'OccupationID',
    'ProductTypeID', 'LocationID', 'FamilyAssets', 'Purchased'
])

# Save as CSV
os.makedirs('data/raw', exist_ok=True)
df.to_csv(save_path, index=False)

print(f"✅ Dataset generation complete! Saved to {save_path}")