from pydantic import BaseModel, Field

class NominalAccountBase(BaseModel):
    external_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)

class NominalAccountCreate(NominalAccountBase):
    pass

class NominalAccountResponse(NominalAccountBase):
    id: int

    class Config:
        from_attributes = True