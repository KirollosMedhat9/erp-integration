from pydantic import BaseModel, Field

class DepartmentBase(BaseModel):
    external_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    version: int = Field(..., ge=1)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True