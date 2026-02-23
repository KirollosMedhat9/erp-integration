from app.db.session import Base

class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Base.Column(Base.Integer, primary_key=True)

    invoice_id = Base.Column(
        Base.Integer,
        Base.ForeignKey("invoices.id"),
        nullable=False
    )

    nominal_account_id = Base.Column(
        Base.Integer,
        Base.ForeignKey("nominal_accounts.id"),
        nullable=False
    )

    department_id = Base.Column(
        Base.Integer,
        Base.ForeignKey("departments.id"),
        nullable=True
    )

    tax_code_id = Base.Column(
        Base.Integer,
        Base.ForeignKey("tax_codes.id"),
        nullable=True
    )

    description = Base.Column(Base.String(255))
    amount = Base.Column(Base.Float, nullable=False)

    # Relationships
    nominal_account = Base.relationship("NominalAccount")
    department = Base.relationship("Department")
    tax_code = Base.relationship("TaxCode")