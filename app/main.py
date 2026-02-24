from fastapi import FastAPI
from app.db.session import engine, Base
from app.routers import vendor_router
from app.routers import tax_code_router
from app.routers import nominal_account_router
from app.routers import department_router
from app.routers import invoice_router

# Create all database tables based on SQLAlchemy models
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ERP Integration API")

app.include_router(vendor_router.router)
app.include_router(tax_code_router.router)
app.include_router(nominal_account_router.router)
app.include_router(department_router.router)
app.include_router(invoice_router.router)