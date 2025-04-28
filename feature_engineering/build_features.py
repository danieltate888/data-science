import pandas as pd
import os

# // 创建处理后数据目录
os.makedirs('data/processed', exist_ok=True)

# // 载入清洗后的原始数据
raw_df = pd.read_csv('data/raw/dataset.csv')

# // 显示数据基本信息
print("原始数据：")
print(raw_df.head())

# // 检查是否有缺失值
print("缺失值检查：")
print(raw_df.isnull().sum())

# // 性别编码：Male -> 0, Female -> 1
raw_df['Gender'] = raw_df['Gender'].map({'Male': 0, 'Female': 1})

# // 职业独热编码（One-Hot Encoding）
raw_df = pd.get_dummies(raw_df, columns=['Occupation'])

# // 划分特征X和目标y
X = raw_df.drop('Purchased', axis=1)
y = raw_df['Purchased']

# // 保存处理后的特征和标签
X.to_csv('data/processed/train_features.csv', index=False)
y.to_csv('data/processed/train_labels.csv', index=False)

print("✅ 特征工程完成，生成 train_features.csv 和 train_labels.csv")