from pydantic import BaseModel, Field


class Case_Price_Model(BaseModel):
    name: str = Field(max_length=25)
    price: float = Field()

