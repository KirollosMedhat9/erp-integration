from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.vendor_schema import VendorCreate, VendorResponse
from app.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_200_OK
)
def upsert_vendor(
    payload: VendorCreate,
    db: Session = Depends(get_db)
):
    service = VendorService(db)
    return service.upsert_vendor(payload)