from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.invoice_import_service import InvoiceImportService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

@router.post("/invoices/import-csv")
def import_invoices(db: Session = Depends(get_db)):
    service = InvoiceImportService(db)
    df = service.load_csv("dataset/line_items.csv")
    service.upsert_master_data(df)
    service.import_invoices(df)
    return {"message": f"{len(df)} rows imported successfully."}