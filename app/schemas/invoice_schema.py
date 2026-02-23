from pydantic import BaseModel, Field
from typing import List
from datetime import date

class InvoiceLineCreate(BaseModel):
    description: str = Field(..., min_length=1)
    net_amount: float = Field(..., gt=0)
    vat_amount: float = Field(..., ge=0)
    tax_code_external_id: str
    nominal_external_id: str
    department_external_id: str

class InvoiceCreate(BaseModel):
    external_invoice_id: str = Field(..., min_length=1)
    vendor_external_id: str
    invoice_date: date
    lines: List[InvoiceLineCreate]