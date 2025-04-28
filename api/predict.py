import pickle
import numpy as np
import yaml
import os

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

BEST_THRESHOLD = config.get('best_threshold', 0.5)

# 加载模型和特征
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'purchase_model.pkl')
feature_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'feature_list.pkl')
scaler_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl')

with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(feature_path, 'rb') as f:
    feature_list = pickle.load(f)

with open(scaler_path, 'rb') as f:
    scaler = pickle.load(f)

# 读入映射字典
gender_dict = config['gender_dict']
occupation_dict = config['occupation_dict']
product_type_dict = config['product_type_dict']
location_dict = config['location_dict']

# 预处理输入
def preprocess_input(data):
    processed = {}

    # 直接数值特征
    processed['Age'] = data['Age']
    processed['AnnualIncome'] = data['AnnualIncome']
    processed['FamilyAssets'] = data['FamilyAssets']

    # 新增衍生特征
    processed['AgeLevel'] = 1 if data['Age'] < 18 else 0
    processed['AssetLevel'] = 1 if data['FamilyAssets'] < 200000 else 0

    # 映射ID
    gender = gender_dict.get(data['GenderID'])
    if gender is None:
        raise ValueError(f"Invalid GenderID: {data['GenderID']}")

    occupation = occupation_dict.get(data['OccupationID'])
    if occupation is None:
        raise ValueError(f"Invalid OccupationID: {data['OccupationID']}")

    product_type = product_type_dict.get(data['ProductTypeID'])
    if product_type is None:
        raise ValueError(f"Invalid ProductTypeID: {data['ProductTypeID']}")

    location = location_dict.get(data['LocationID'])
    if location is None:
        raise ValueError(f"Invalid LocationID: {data['LocationID']}")

    # One-hot编码
    for col in feature_list:
        if col.startswith('Gender_'):
            processed[col] = 1 if col == f'Gender_{gender}' else 0
        elif col.startswith('Occupation_'):
            processed[col] = 1 if col == f'Occupation_{occupation}' else 0
        elif col.startswith('ProductType_'):
            processed[col] = 1 if col == f'ProductType_{product_type}' else 0
        elif col.startswith('Location_'):
            processed[col] = 1 if col == f'Location_{location}' else 0

    # 数值归一化
    numerical_features = ['Age', 'AnnualIncome', 'FamilyAssets']
    processed_array = np.array([processed.get(col, 0) for col in feature_list]).reshape(1, -1)

    if scaler:
        indices = [feature_list.index(f) for f in numerical_features]
        processed_array[:, indices] = scaler.transform(processed_array[:, indices])

    return processed_array

# 预测函数
def predict_purchase(data):
    input_array = preprocess_input(data)
    proba = model.predict_proba(input_array)[0][1]  # 预测类别1的概率
    prediction = int(proba >= BEST_THRESHOLD)      # 根据最佳阈值分类
    return {
        "Purchased": prediction,
        "Probability": round(float(proba), 4)
    }