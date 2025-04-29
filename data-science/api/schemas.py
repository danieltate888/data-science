# api/schemas.py

from pydantic import BaseModel

# 定义前端传过来的请求格式
class PurchaseRequest(BaseModel):
    Age: int
    GenderID: int
    AnnualIncome: int
    OccupationID: int
    ProductTypeID: int
    LocationID: int
    FamilyAssets: int
