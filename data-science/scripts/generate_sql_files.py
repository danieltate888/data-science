# scripts/generate_sql_files.py

import pandas as pd
import numpy as np
import random
import os
from faker import Faker

# Initialize Faker
faker = Faker()

# Output directory for SQL files
save_dir = 'data/sql'
os.makedirs(save_dir, exist_ok=True)

# Define lookup dictionaries
gender_dict = {0: 'Male', 1: 'Female'}
occupation_dict = {
    0: "Engineer", 1: "Artist", 2: "Doctor", 3: "Teacher", 4: "Sales",
    5: "Lawyer", 6: "Scientist", 7: "Accountant", 8: "Nurse", 9: "Software Developer"
}
product_type_dict = {
    0: "Laptop", 1: "Smartphone", 2: "Camera", 3: "Cosmetics", 4: "Handbag",
    5: "Shoes", 6: "TV", 7: "Perfume", 8: "Watch", 9: "Clothes"
}
location_dict = {
    0: "Sydney", 1: "Melbourne", 2: "Brisbane", 3: "Perth",
    4: "Adelaide", 5: "Hobart", 6: "Darwin", 7: "Canberra"
}

# Parameters for synthetic label generation
big_cities = [0, 1, 2]
product_hotness = {0: 0.9, 1: 0.9, 2: 0.8, 3: 0.6, 4: 0.7, 5: 0.6, 6: 0.8, 7: 0.5, 8: 0.7, 9: 0.6}
occupation_influence = {0: 0.8, 1: 0.7, 2: 0.9, 3: 0.6, 4: 0.6, 5: 0.7, 6: 0.85, 7: 0.65, 8: 0.5, 9: 0.85}

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate synthetic user and order data
users = []
orders = []

for user_id in range(1, 10001):
    Age = np.random.randint(0, 81)
    GenderID = np.random.randint(0, 2)
    AnnualIncome = np.random.randint(10000, 250001)
    OccupationID = random.choice(list(occupation_dict.keys()))
    ProductTypeID = random.choice(list(product_type_dict.keys()))
    LocationID = random.choice(list(location_dict.keys()))

    # Estimate assets
    asset_multiplier = np.random.uniform(5, 20)
    FamilyAssets = int(AnnualIncome * asset_multiplier + np.random.normal(0, 50000))
    FamilyAssets = max(10000, FamilyAssets)

    Name = faker.name().replace("'", "''")

    # Score calculation based on user profile
    score = 50
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

    if AnnualIncome < 40000:
        score -= 25
    elif AnnualIncome > 120000:
        score += 20

    if FamilyAssets < 100000:
        score -= 30
    elif FamilyAssets > 1000000:
        score += 25

    if GenderID == 0 and ProductTypeID in [0, 1, 2, 6, 8]:
        score += 15
    if GenderID == 1 and ProductTypeID in [3, 4, 5, 7, 9]:
        score += 15

    if LocationID in big_cities:
        score += 5
    else:
        score -= 5

    score += (product_hotness.get(ProductTypeID, 0.6) - 0.6) * 20
    score += (occupation_influence.get(OccupationID, 0.7) - 0.7) * 20
    score += np.random.normal(0, 10)

    # Convert score to purchase probability
    prob = 1 / (1 + np.exp(-0.12 * (score - 50)))
    prob = np.clip(prob, 0.01, 0.99)

    Purchased = np.random.binomial(1, prob)

    users.append((user_id, Name, Age, GenderID, LocationID, OccupationID, FamilyAssets, AnnualIncome))
    purchase_date = faker.date_between(start_date='-3y', end_date='today')
    orders.append((user_id, ProductTypeID, product_type_dict[ProductTypeID], purchase_date, Purchased))

# Write users.sql
with open(os.path.join(save_dir, 'users.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS users;
            CREATE TABLE users (
                                   id SERIAL PRIMARY KEY,
                                   name VARCHAR(255),
                                   age INT,
                                   gender_id INT,
                                   location_id INT,
                                   occupation_id INT,
                                   family_assets BIGINT,
                                   annual_income BIGINT
            );
            INSERT INTO users (id, name, age, gender_id, location_id, occupation_id, family_assets, annual_income) VALUES
            """)
    for idx, row in enumerate(users):
        line = f"({row[0]}, '{row[1]}', {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]})"
        f.write(line + (",\n" if idx < len(users) - 1 else ";\n"))

# Write orders.sql
with open(os.path.join(save_dir, 'orders.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS orders;
            CREATE TABLE orders (
                                    id SERIAL PRIMARY KEY,
                                    user_id INT,
                                    product_type_id INT,
                                    product_name VARCHAR(255),
                                    purchase_date DATE,
                                    purchased INT
            );
            INSERT INTO orders (user_id, product_type_id, product_name, purchase_date, purchased) VALUES
            """)
    for idx, row in enumerate(orders):
        line = f"({row[0]}, {row[1]}, '{row[2]}', '{row[3]}', {row[4]})"
        f.write(line + (",\n" if idx < len(orders) - 1 else ";\n"))

# Write genders.sql
with open(os.path.join(save_dir, 'genders.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS genders;
            CREATE TABLE genders (
                                     id INT PRIMARY KEY,
                                     name VARCHAR(50)
            );
            INSERT INTO genders (id, name) VALUES
                                               (0, 'Male'),
                                               (1, 'Female');
            """)

# Write locations.sql
with open(os.path.join(save_dir, 'locations.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS locations;
            CREATE TABLE locations (
                                       id INT PRIMARY KEY,
                                       name VARCHAR(100)
            );
            INSERT INTO locations (id, name) VALUES
            """)
    for idx, (loc_id, loc_name) in enumerate(location_dict.items()):
        f.write(f"({loc_id}, '{loc_name}')" + (",\n" if idx < len(location_dict) - 1 else ";\n"))

# Write products.sql
with open(os.path.join(save_dir, 'products.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS products;
            CREATE TABLE products (
                                      id INT PRIMARY KEY,
                                      name VARCHAR(100)
            );
            INSERT INTO products (id, name) VALUES
            """)
    for idx, (prod_id, prod_name) in enumerate(product_type_dict.items()):
        f.write(f"({prod_id}, '{prod_name}')" + (",\n" if idx < len(product_type_dict) - 1 else ";\n"))

# Write occupations.sql
with open(os.path.join(save_dir, 'occupations.sql'), 'w') as f:
    f.write("""
            DROP TABLE IF EXISTS occupations;
            CREATE TABLE occupations (
                                         id INT PRIMARY KEY,
                                         name VARCHAR(100)
            );
            INSERT INTO occupations (id, name) VALUES
            """)
    for idx, (occ_id, occ_name) in enumerate(occupation_dict.items()):
        f.write(f"({occ_id}, '{occ_name}')" + (",\n" if idx < len(occupation_dict) - 1 else ";\n"))

print("✅ All SQL files successfully generated in the data/sql directory.")