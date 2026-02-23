from sqlalchemy.orm import Session
from app.models.tax_code import TaxCode
from app.schemas.tax_code_schema import TaxCodeCreate

class TaxCodeService:

    def __init__(self, db: Session):
        self.db = db

    def upsert_tax_code(self, payload: TaxCodeCreate) -> TaxCode:
        tax_code = (
            self.db.query(TaxCode)
            .filter(TaxCode.external_id == payload.external_id)
            .first()
        )

        # CREATE
        if not tax_code:
            tax_code = TaxCode(
                external_id=payload.external_id,
                rate=payload.rate,
                version=payload.version
            )
            self.db.add(tax_code)
            self.db.commit()
            self.db.refresh(tax_code)
            return tax_code

        # IDEMPOTENCY
        if payload.version <= tax_code.version:
            return tax_code

        # UPDATE
        tax_code.rate = payload.rate
        tax_code.version = payload.version

        self.db.commit()
        self.db.refresh(tax_code)
        return tax_code