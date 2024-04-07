from pydantic import BaseModel, Field


class CasePriceModel(BaseModel):
    name: str = Field(max_length=50)
    price: float = Field()

