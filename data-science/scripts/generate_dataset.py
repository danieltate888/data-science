# scripts/generate_enterprise_dataset.py

import pandas as pd
import numpy as np
import random
import os

# 配置保存路径
save_path = 'data/raw/dataset.csv'

# 基础配置
occupations = list(range(10))  # 职业ID：0-9
product_types = list(range(10))  # 商品ID：0-9
locations = list(range(8))  # 城市ID：0-7

# 大城市 vs 小城市
big_cities = [0, 1, 2]  # Sydney, Melbourne, Brisbane
small_cities = [3, 4, 5, 6, 7]

# 商品热度（小结：美妆/包/鞋子热度较低）
product_hotness = {
    0: 0.9,  # Laptop
    1: 0.9,  # Smartphone
    2: 0.8,  # Camera
    3: 0.6,  # Cosmetics
    4: 0.7,  # Handbag
    5: 0.6,  # Shoes
    6: 0.8,  # TV
    7: 0.5,  # Perfume
    8: 0.7,  # Watch
    9: 0.6   # Clothes
}

# 职业比重分：有些职业对购买有更大影响
occupation_influence = {
    0: 0.8,  # Engineer
    1: 0.7,  # Artist
    2: 0.9,  # Doctor
    3: 0.6,  # Teacher
    4: 0.6,  # Sales
    5: 0.7,  # Lawyer
    6: 0.85, # Scientist
    7: 0.65, # Accountant
    8: 0.5,  # Nurse
    9: 0.85  # Software Developer
}

# 设置随机种子，可复现
np.random.seed(42)
random.seed(42)

# 生成5000条数据
samples = []
for _ in range(5000):
    Age = np.random.randint(0, 81)
    GenderID = np.random.randint(0, 2)
    AnnualIncome = np.random.randint(10000, 250001)
    OccupationID = random.choice(occupations)
    ProductTypeID = random.choice(product_types)
    LocationID = random.choice(locations)

    # 先计算家庭财产：年收入的 5-20倍，有随机振荡
    asset_multiplier = np.random.uniform(5, 20)
    FamilyAssets = int(AnnualIncome * asset_multiplier + np.random.normal(0, 50000))
    FamilyAssets = max(10000, FamilyAssets)  # 防止资产为负

    # 计算基础分（起始50）
    score = 50

    # Age影响
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

    # Income影响
    if AnnualIncome < 40000:
        score -= 25
    elif AnnualIncome > 120000:
        score += 20

    # Assets影响
    if FamilyAssets < 100000:
        score -= 30
    elif FamilyAssets > 1000000:
        score += 25

    # Gender + ProductType偏好影响
    if GenderID == 0 and ProductTypeID in [0, 1, 2, 6, 8]:
        score += 15
    if GenderID == 1 and ProductTypeID in [3, 4, 5, 7, 9]:
        score += 15

    # 大城市优势
    if LocationID in big_cities:
        score += 5
    else:
        score -= 5

    # 商品热度加分
    score += (product_hotness.get(ProductTypeID, 0.6) - 0.6) * 20

    # 职业影响加分
    score += (occupation_influence.get(OccupationID, 0.7) - 0.7) * 20

    # 随机权重异差，模拟真实人类不精确行为
    score += np.random.normal(0, 10)

    # 将分数折缩到[0,1] 范围，计算购买概率
    prob = 1 / (1 + np.exp(-0.12 * (score - 50)))

    # 根据概率投掷，删除过分坑一些
    prob = np.clip(prob, 0.01, 0.99)

    Purchased = np.random.binomial(1, prob)

    samples.append([
        Age, GenderID, AnnualIncome, OccupationID, ProductTypeID, LocationID, FamilyAssets, Purchased
    ])

# 生成DataFrame
df = pd.DataFrame(samples, columns=[
    'Age', 'GenderID', 'AnnualIncome', 'OccupationID', 'ProductTypeID', 'LocationID', 'FamilyAssets', 'Purchased'
])

# 保存CSV
os.makedirs('data/raw', exist_ok=True)
df.to_csv(save_path, index=False)

print(f"✅ 数据集生成完成！已保存到 {save_path}")