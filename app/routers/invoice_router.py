from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.invoice_service import InvoiceService
from app.schemas.invoice_schema import InvoiceCreate

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db)
):
    service = InvoiceService(db)
    return service.create_invoice(payload)