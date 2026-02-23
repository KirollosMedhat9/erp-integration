from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.department_schema import (
    DepartmentCreate,
    DepartmentResponse
)
from app.services.department_service import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK
)
def upsert_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db)
):
    service = DepartmentService(db)
    return service.upsert_department(payload)