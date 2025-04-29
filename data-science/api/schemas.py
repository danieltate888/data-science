from pydantic import BaseModel

class PurchaseRequest(BaseModel):
    age: int
    gender_id: int
    annual_income: float
    occupation_id: int
    product_type_id: int
    location_id: int
    family_assets: float