import pandas as pd
import pickle
import os
import numpy as np
import yaml
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

# 读取特征和标签
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# 分割训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 读取已训练好的模型
model_path = os.path.join('models', 'purchase_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# 读取 config 文件，获取最优Threshold
config_path = 'config/config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

best_threshold = config.get('best_threshold', 0.5)

# 在验证集上预测概率
y_val_probs = model.predict_proba(X_val)[:, 1]

# 根据最优阅值，手动分类
y_val_pred = (y_val_probs >= best_threshold).astype(int)

# 计算指标
accuracy = accuracy_score(y_val, y_val_pred)
precision = precision_score(y_val, y_val_pred)
recall = recall_score(y_val, y_val_pred)
f1 = f1_score(y_val, y_val_pred)

# 打印结果
print("\n✅ 基于最优Threshold评估模型结果：")
print(f"Best Threshold used: {best_threshold:.4f}")
print(f"Accuracy (准确率): {accuracy:.4f}")
print(f"Precision (精确率): {precision:.4f}")
print(f"Recall (召回率): {recall:.4f}")
print(f"F1 Score: {f1:.4f}\n")
