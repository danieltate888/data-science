from flask import Flask, request, jsonify
from predict import predict_purchase  # 导入预测函数

# // 创建Flask应用
app = Flask(__name__)

# // 定义预测接口
@app.route('/predict', methods=['POST'])
def predict_api():
    """
    接收POST请求，调用predict.py里的predict_purchase函数，返回预测结果
    """
    data = request.get_json()

    try:
        prediction = predict_purchase(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"Purchased": prediction})

# // 启动Flask服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)