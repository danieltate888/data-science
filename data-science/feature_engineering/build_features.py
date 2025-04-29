import pandas as pd
import yaml
import os
import pickle
from sklearn.preprocessing import StandardScaler

# 读取配置
def load_config(path='config/config.yaml'):
    with open(path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# 创建目录
os.makedirs('data/processed', exist_ok=True)
os.makedirs('models', exist_ok=True)

# 读取原始数据
raw_df = pd.read_csv('data/raw/dataset.csv')
print("原始数据：")
print(raw_df.head())

# 读取字典
config = load_config()
gender_map = config['gender_dict']
occupation_map = config['occupation_dict']
product_map = config['product_type_dict']
location_map = config['location_dict']

# ID映射
raw_df['Gender'] = raw_df['GenderID'].map(gender_map)
raw_df['Occupation'] = raw_df['OccupationID'].map(occupation_map)
raw_df['ProductType'] = raw_df['ProductTypeID'].map(product_map)
raw_df['Location'] = raw_df['LocationID'].map(location_map)

# 删除原ID
raw_df.drop(['GenderID', 'OccupationID', 'ProductTypeID', 'LocationID'], axis=1, inplace=True)

# 新增衍生特征：AgeLevel和AssetLevel
raw_df['AgeLevel'] = raw_df['Age'].apply(lambda x: 1 if x < 18 else 0)
raw_df['AssetLevel'] = raw_df['FamilyAssets'].apply(lambda x: 1 if x < 200000 else 0)

# One-Hot编码
raw_df = pd.get_dummies(raw_df, columns=['Gender', 'Occupation', 'ProductType', 'Location'])

# 分割X和y
X = raw_df.drop('Purchased', axis=1)
y = raw_df['Purchased']

# 对数值特征标准化
numerical_features = ['Age', 'AnnualIncome', 'FamilyAssets']
scaler = StandardScaler()
X[numerical_features] = scaler.fit_transform(X[numerical_features])

# 保存特征和标签
X.to_csv('data/processed/train_features.csv', index=False)
y.to_csv('data/processed/train_labels.csv', index=False)

# 保存scaler对象
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("\u2705 特征工程完成：标准化 + 衍生特征生成")
