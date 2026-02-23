from pydantic import BaseModel, Field

class TaxCodeBase(BaseModel):
    external_id: str = Field(..., min_length=1)
    rate: float = Field(..., ge=0)

class TaxCodeCreate(TaxCodeBase):
    version: int = Field(..., ge=1)

class TaxCodeResponse(TaxCodeBase):
    id: int
    version: int

    class Config:
        from_attributes = True