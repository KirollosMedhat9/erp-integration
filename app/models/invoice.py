from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, ForeignKey, DateTime, func
from app.db.session import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_invoice_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"), nullable=False)
    invoice_date: Mapped[Date] = mapped_column(Date, nullable=False)
    total_net: Mapped[float] = mapped_column(Float, default=0.0)
    total_vat: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationship to lines
    lines = relationship("InvoiceLine", back_populates="invoice")

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, external_invoice_id='{self.external_invoice_id}', vendor_id={self.vendor_id})>"


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    vat_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_code_id: Mapped[int] = mapped_column(ForeignKey("tax_codes.id"), nullable=False)
    nominal_account_id: Mapped[int] = mapped_column(ForeignKey("nominal_accounts.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    invoice = relationship("Invoice", back_populates="lines")

    def __repr__(self) -> str:
        return f"<InvoiceLine(id={self.id}, invoice_id={self.invoice_id}, description='{self.description}')>"