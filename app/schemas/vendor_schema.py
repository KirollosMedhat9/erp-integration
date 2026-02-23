from pydantic import BaseModel, Field
from typing import Optional

class VendorBase(BaseModel):
    external_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)

class VendorCreate(VendorBase):
    pass

class VendorResponse(VendorBase):
    id: int

    class Config:
        from_attributes = True