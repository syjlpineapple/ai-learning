from pydantic import BaseModel, Field


class ProductRequest(BaseModel):
    product_name:str
    price:float = Field(ge=0)
    platform:str

