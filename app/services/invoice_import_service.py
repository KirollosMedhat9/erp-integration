from typing import Optional, cast
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.vendor import Vendor
from app.models.tax_code import TaxCode
from app.models.nominal_account import NominalAccount
from app.models.department import Department
from app.models.invoice import Invoice, InvoiceLine


class InvoiceImportService:
    def __init__(self, db: Session):
        self.db = db

    def load_csv(self, path: str) -> pd.DataFrame:
        """Load the CSV dataset into a DataFrame."""
        try:
            df = pd.read_csv(path, sep=",", engine="python")  # use the correct separator
            df.columns = df.columns.str.strip()  # remove any extra spaces
            print("Columns detected:", df.columns.tolist())
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to load CSV: {e}")

    def upsert_master_data(self, df: pd.DataFrame):
        """Create or update Vendors, TaxCodes, NominalAccounts, Departments."""

        # 1️⃣ Vendors
               
        for v_name in df["SUPPLIER"].unique():
            existing_vendor: Optional[Vendor] = self.db.query(Vendor).filter(Vendor.external_id == v_name).first()
            if not existing_vendor:
                self.db.add(Vendor(external_id=v_name, name=v_name))
        self.db.commit()

        # 2️⃣ Tax Codes
        for tc in df["TC"].unique():
            existing_tax_code: Optional[TaxCode] = self.db.query(TaxCode).filter(TaxCode.external_id == tc).first()
            if not existing_tax_code:
                self.db.add(TaxCode(external_id=tc, rate=0.0))
        self.db.commit()

        # 3️⃣ Nominal Accounts
        for n in df["NOMINAL"].unique():
            existing_nominal: Optional[NominalAccount] = self.db.query(NominalAccount).filter(NominalAccount.external_id == n).first()
            if not existing_nominal:
                self.db.add(NominalAccount(external_id=n, name=n))
        self.db.commit()

        # 4️⃣ Departments
        for d in df["DEPARTMENT"].unique():
            existing_department: Optional[Department] = self.db.query(Department).filter(Department.external_id == d).first()
            if not existing_department:
                self.db.add(Department(external_id=d, name=d))

        self.db.commit()

        # 4️⃣ Departments
        for d in df["DEPARTMENT"].unique():
            existing: Optional[Department] = self.db.query(Department).filter(Department.external_id == d).first()
            if not existing:
                self.db.add(Department(external_id=d, name=d))
        self.db.commit()

    def import_invoices(self, df: pd.DataFrame):
        """Import invoices and lines grouped by REF."""
        for ref, group in df.groupby("REF"):
            external_invoice_id = str(ref)

            # Idempotency: skip if invoice already exists
            existing_invoice: Optional[Invoice] = self.db.query(Invoice).filter(Invoice.external_invoice_id == external_invoice_id).first()
            if existing_invoice:
                continue

            # Vendor for this invoice
            vendor_name = group.iloc[0]["SUPPLIER"]
            vendor: Optional[Vendor] = self.db.query(Vendor).filter(Vendor.external_id == vendor_name).first()
            if not vendor:
                raise ValueError(f"Vendor '{vendor_name}' not found for invoice REF {ref}")

            # Parse invoice date
            invoice_date = datetime.strptime(group.iloc[0]["DATE"], "%m/%d/%Y").date()

            invoice = Invoice(
                external_invoice_id=external_invoice_id,
                vendor_id=vendor.id,
                invoice_date=invoice_date,
                total_net=0.0,
                total_vat=0.0
            )
            self.db.add(invoice)
            self.db.flush()  # assign invoice.id before adding lines

            total_net = 0.0
            total_vat = 0.0

            for _, row in group.iterrows():
                # Lookup master data
                tax_code: Optional[TaxCode] = self.db.query(TaxCode).filter(TaxCode.external_id == row["TC"]).first()
                nominal: Optional[NominalAccount] = self.db.query(NominalAccount).filter(NominalAccount.external_id == row["NOMINAL"]).first()
                department: Optional[Department] = self.db.query(Department).filter(Department.external_id == row["DEPARTMENT"]).first()

                if not all([tax_code, nominal, department]):
                    raise ValueError(f"Missing master data for invoice REF {ref}, line: {row.to_dict()}")

                # Cast to suppress Pylance warning
                tax_code = cast(TaxCode, tax_code)
                nominal = cast(NominalAccount, nominal)
                department = cast(Department, department)

                net_amount = float(row["NET"])
                vat_amount = float(row["VAT"])
                total_net += net_amount
                total_vat += vat_amount

                line = InvoiceLine(
                    invoice_id=invoice.id,
                    description=row["DETAIL"],
                    net_amount=net_amount,
                    vat_amount=vat_amount,
                    tax_code_id=tax_code.id,
                    nominal_account_id=nominal.id,
                    department_id=department.id
                )
                self.db.add(line)

            invoice.total_net = total_net
            invoice.total_vat = total_vat

        # Commit all invoices + lines in a single atomic transaction
        self.db.commit()