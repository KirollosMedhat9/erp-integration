from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.invoice import Invoice
from app.models.invoice_line import InvoiceLine
from app.models.vendor import Vendor
from app.models.tax_code import TaxCode 
from app.models.nominal_account import NominalAccount
from app.models.department import Department
from app.schemas.invoice_schema import InvoiceCreate

class InvoiceService:

    def __init__(self, db: Session):
        self.db = db

    def create_invoice(self, payload: InvoiceCreate):

        # Duplicate detection (idempotency)
        existing = (
            self.db.query(Invoice)
            .filter(Invoice.external_invoice_id == payload.external_invoice_id)
            .first()
        )

        if existing:
            return existing

        # Validate vendor
        vendor = (
            self.db.query(Vendor)
            .filter(Vendor.external_id == payload.vendor_external_id)
            .first()
        )

        if not vendor:
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": "VENDOR_NOT_FOUND",
                    "message": f"Vendor {payload.vendor_external_id} not found"
                }
            )

        # Atomic transaction
        try:
            with self.db.begin():

                invoice = Invoice(
                    external_invoice_id=payload.external_invoice_id,
                    vendor_id=vendor.id,
                    invoice_date=payload.invoice_date
                )
                self.db.add(invoice)
                self.db.flush()  # get invoice.id

                for idx, line in enumerate(payload.lines):

                    tax_code = self.db.query(TaxCode).filter(
                        TaxCode.external_id == line.tax_code_external_id
                    ).first()

                    if not tax_code:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error_code": "INVALID_TAX_CODE",
                                "message": f"Tax code {line.tax_code_external_id} not found",
                                "line": idx + 1
                            }
                        )

                    account = self.db.query(NominalAccount).filter(
                        NominalAccount.external_id == line.nominal_external_id
                    ).first()

                    if not account:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error_code": "INVALID_ACCOUNT",
                                "message": f"Account {line.nominal_external_id} not found",
                                "line": idx + 1
                            }
                        )

                    department = self.db.query(Department).filter(
                        Department.external_id == line.department_external_id
                    ).first()

                    if not department:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error_code": "INVALID_DEPARTMENT",
                                "message": f"Department {line.department_external_id} not found",
                                "line": idx + 1
                            }
                        )

                    # VAT validation
                    expected_vat = round(line.net_amount * tax_code.rate, 2)
                    if round(line.vat_amount, 2) != expected_vat:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error_code": "VAT_MISMATCH",
                                "message": f"VAT incorrect on line {idx+1}",
                                "expected": expected_vat,
                                "received": line.vat_amount
                            }
                        )

                    invoice_line = InvoiceLine(
                        invoice_id=invoice.id,
                        description=line.description,
                        net_amount=line.net_amount,
                        vat_amount=line.vat_amount,
                        tax_code_id=tax_code.id,
                        nominal_account_id=account.id,
                        department_id=department.id
                    )

                    self.db.add(invoice_line)

            return invoice

        except HTTPException:
            self.db.rollback()
            raise