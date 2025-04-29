from fastapi import FastAPI, HTTPException
from api.schemas import PurchaseRequest
from api.predict import predict_purchase

# Create FastAPI application instance
app = FastAPI()

# Define prediction API endpoint
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