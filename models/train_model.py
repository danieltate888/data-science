import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle
import os

# // 载入处理好的特征和标签
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# // 建立并训练Logistic Regression模型
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# // 创建models目录
os.makedirs('models', exist_ok=True)

# // 保存模型
with open('models/purchase_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# // 保存特征列
feature_list = list(X.columns)
with open('models/feature_list.pkl', 'wb') as f:
    pickle.dump(feature_list, f)

print("✅ 模型训练完成并已保存到 models/ (purchase_model.pkl, feature_list.pkl)")