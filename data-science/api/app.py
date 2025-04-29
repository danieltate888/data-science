from fastapi import FastAPI, HTTPException
from api.schemas import PurchaseRequest
from api.predict import predict_purchase

# 创建FastAPI应用
app = FastAPI()

# 定义预测接口
@app.post("/predict")
def predict_api(request: PurchaseRequest):
    try:
        data = request.dict()
        result = predict_purchase(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")