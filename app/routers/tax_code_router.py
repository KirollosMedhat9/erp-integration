from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.tax_code_schema import TaxCodeCreate, TaxCodeResponse
from app.services.tax_code_service import TaxCodeService

router = APIRouter(prefix="/tax-codes", tags=["Tax Codes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "",
    response_model=TaxCodeResponse,
    status_code=status.HTTP_200_OK
)
def upsert_tax_code(
    payload: TaxCodeCreate,
    db: Session = Depends(get_db)
):
    service = TaxCodeService(db)
    return service.upsert_tax_code(payload)