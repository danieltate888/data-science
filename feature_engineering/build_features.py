# import pandas as pd
# import os
#
# # // 创建处理后数据目录
# os.makedirs('data/processed', exist_ok=True)
#
# # // 载入清洗后的原始数据
# raw_df = pd.read_csv('data/raw/dataset1.csv')
#
# # // 显示数据基本信息
# print("原始数据：")
# print(raw_df.head())
#
# # // 检查是否有缺失值
# print("缺失值检查：")
# print(raw_df.isnull().sum())
#
# # // 性别编码：Male -> 0, Female -> 1
# raw_df['Gender'] = raw_df['Gender'].map({'Male': 0, 'Female': 1})
#
# # // 职业独热编码（One-Hot Encoding）
# raw_df = pd.get_dummies(raw_df, columns=['Occupation'])
#
# # // 划分特征X和目标y
# X = raw_df.drop('Purchased', axis=1)
# y = raw_df['Purchased']
#
# # // 保存处理后的特征和标签
# X.to_csv('data/processed/train_features.csv', index=False)
# y.to_csv('data/processed/train_labels.csv', index=False)
#
# print("✅ 特征工程完成，生成 train_features.csv 和 train_labels.csv")


# Updated feature engineering script
# import pandas as pd
# import yaml
# import os
#
# # 读取配置文件
# def load_config(path='config/config.yaml'):
#     with open(path, 'r') as file:
#         config = yaml.safe_load(file)
#     return config
#
# # 创建处理后数据目录
# os.makedirs('data/processed', exist_ok=True)
#
# # 读取原始数据
# raw_df = pd.read_csv('data/raw/dataset.csv')
# print("原始数据：")
# print(raw_df.head())
#
# # 读取字典配置
# config = load_config()
# gender_map = config['gender_dict']
# occupation_map = config['occupation_dict']
# product_map = config['product_type_dict']
# location_map = config['location_dict']
#
# # ID 映射成名称
# raw_df['Gender'] = raw_df['GenderID'].map(gender_map)
# raw_df['Occupation'] = raw_df['OccupationID'].map(occupation_map)
# raw_df['ProductType'] = raw_df['ProductTypeID'].map(product_map)
# raw_df['Location'] = raw_df['LocationID'].map(location_map)
#
# # 删除原始ID列
# raw_df.drop(['GenderID', 'OccupationID', 'ProductTypeID', 'LocationID'], axis=1, inplace=True)
#
# # 进行One-Hot编码：Gender, Occupation, ProductType, Location
# raw_df = pd.get_dummies(raw_df, columns=['Gender', 'Occupation', 'ProductType', 'Location'])
#
# # 分割特征X和标签列y
# X = raw_df.drop('Purchased', axis=1)
# y = raw_df['Purchased']
#
# # 保存处理好的特征和标签
# X.to_csv('data/processed/train_features.csv', index=False)
# y.to_csv('data/processed/train_labels.csv', index=False)
#
# print("\u2705 特征工程完成，生成 train_features.csv 和 train_labels.csv")

# V3
# feature_engineering/build_features.py

# import pandas as pd
# import yaml
# import os
# import pickle
# from sklearn.preprocessing import StandardScaler
#
# # 读取配置
#
# def load_config(path='config/config.yaml'):
#     with open(path, 'r') as file:
#         config = yaml.safe_load(file)
#     return config
#
# # 创建目录
# os.makedirs('data/processed', exist_ok=True)
# os.makedirs('models', exist_ok=True)
#
# # 读取原始数据
# raw_df = pd.read_csv('data/raw/dataset.csv')
# print("原始数据：")
# print(raw_df.head())
#
# # 读取字典
# config = load_config()
# gender_map = config['gender_dict']
# occupation_map = config['occupation_dict']
# product_map = config['product_type_dict']
# location_map = config['location_dict']
#
# # ID映射
# raw_df['Gender'] = raw_df['GenderID'].map(gender_map)
# raw_df['Occupation'] = raw_df['OccupationID'].map(occupation_map)
# raw_df['ProductType'] = raw_df['ProductTypeID'].map(product_map)
# raw_df['Location'] = raw_df['LocationID'].map(location_map)
#
# # 删除原ID
# raw_df.drop(['GenderID', 'OccupationID', 'ProductTypeID', 'LocationID'], axis=1, inplace=True)
#
# # One-Hot编码
# raw_df = pd.get_dummies(raw_df, columns=['Gender', 'Occupation', 'ProductType', 'Location'])
#
# # 分割X和y
# X = raw_df.drop('Purchased', axis=1)
# y = raw_df['Purchased']
#
# # 对数值特征标准化
# numerical_features = ['Age', 'AnnualIncome', 'FamilyAssets']
# scaler = StandardScaler()
# X[numerical_features] = scaler.fit_transform(X[numerical_features])
#
# # 保存特征和标签
# X.to_csv('data/processed/train_features.csv', index=False)
# y.to_csv('data/processed/train_labels.csv', index=False)
#
# # 保存scaler对象
# with open('models/scaler.pkl', 'wb') as f:
#     pickle.dump(scaler, f)
#
# print("\u2705 特征工程完成，标准化完成，生成 train_features.csv, train_labels.csv, scaler.pkl")

# V4
# feature_engineering/build_features.py (LightGBM版本)

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
