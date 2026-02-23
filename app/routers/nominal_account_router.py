from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.nominal_account_schema import (
    NominalAccountCreate,
    NominalAccountResponse
)
from app.services.nominal_account_service import NominalAccountService

router = APIRouter(prefix="/accounts", tags=["Nominal Accounts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "",
    response_model=NominalAccountResponse,
    status_code=status.HTTP_200_OK
)
def upsert_nominal_account(
    payload: NominalAccountCreate,
    db: Session = Depends(get_db)
):
    service = NominalAccountService(db)
    return service.upsert_nominal_account(payload)