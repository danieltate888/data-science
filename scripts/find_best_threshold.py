import pandas as pd
import pickle
import os
import numpy as np
from sklearn.metrics import precision_recall_curve, f1_score
from sklearn.model_selection import train_test_split
import yaml

# 读取处理好的特征和标签
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# 分割训练集和验证集
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 加载已经训练好的模型
model_path = os.path.join('models', 'purchase_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# 预测预温集概率
y_val_probs = model.predict_proba(X_val)[:, 1]  # 第一列：第0类，第二列：第1类，我们要的是1的概率

# 计算各种间隔阅的 Precision, Recall, Thresholds
precisions, recalls, thresholds = precision_recall_curve(y_val, y_val_probs)

# 计算 F1
f1s = 2 * (precisions * recalls) / (precisions + recalls)

# 找最大的F1分数
best_idx = np.argmax(f1s)
best_threshold = thresholds[best_idx]

print("\n\u2705 自动定位最优阶段：")
print(f"Best Threshold: {best_threshold:.4f}")
print(f"Precision at best threshold: {precisions[best_idx]:.4f}")
print(f"Recall at best threshold: {recalls[best_idx]:.4f}")
print(f"F1 Score at best threshold: {f1s[best_idx]:.4f}\n")

config_path = 'config/config.yaml'

# 先读取原有配置
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# 更新BEST_THRESHOLD字段
config['best_threshold'] = float(best_threshold)

# 写回去
with open(config_path, 'w') as f:
    yaml.dump(config, f)

print(f"✅ 已把最佳阈值 {best_threshold:.4f} 自动写入到 config/config.yaml")