import pickle
import numpy as np
import os

# // 定位到models目录
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'purchase_model.pkl')
feature_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'feature_list.pkl')

# // 加载保存好的模型和特征列表
with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(feature_path, 'rb') as f:
    feature_list = pickle.load(f)

def predict_purchase(data):
    """
    接受字典格式的数据，按照特征顺序处理，并返回预测结果。
    """
    try:
        input_features = [data[feature] for feature in feature_list]
    except KeyError as e:
        raise ValueError(f"Missing feature: {e}")

    input_array = np.array(input_features).reshape(1, -1)
    prediction = model.predict(input_array)[0]

    return int(prediction)