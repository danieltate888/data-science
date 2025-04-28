import pandas as pd
import pickle
import os
import lightgbm as lgb
from sklearn.model_selection import GridSearchCV

# 读取特征和标签
X = pd.read_csv('data/processed/train_features.csv')
y = pd.read_csv('data/processed/train_labels.csv')

# 创建 models 目录
os.makedirs('models', exist_ok=True)

# 定义模型和超参数编译
param_grid = {
    'num_leaves': [15, 31],
    'max_depth': [-1, 10, 20],
    'learning_rate': [0.05, 0.1]
}

lgbm = lgb.LGBMClassifier(random_state=42, is_unbalance=True)

grid_search = GridSearchCV(lgbm, param_grid, cv=3, scoring='f1', n_jobs=-1, verbose=1)
grid_search.fit(X, y.values.ravel())

# 最佳模型
best_model = grid_search.best_estimator_

# 保存模型
with open('models/purchase_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

# 保存特征列
feature_list = list(X.columns)
with open('models/feature_list.pkl', 'wb') as f:
    pickle.dump(feature_list, f)

print("\u2705 模型训练完成：最佳LightGBM模型已保存（purchase_model.pkl）")
