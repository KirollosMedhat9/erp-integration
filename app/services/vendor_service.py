from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from app.schemas.vendor_schema import VendorCreate

class VendorService:

    def __init__(self, db: Session):
        self.db = db

    def upsert_vendor(self, payload: VendorCreate) -> Vendor:
        vendor = (
            self.db.query(Vendor)
            .filter(Vendor.external_id == payload.external_id)
            .first()
        )

        # CREATE
        if not vendor:
            vendor = Vendor(
                external_id=payload.external_id,
                name=payload.name,
                version=payload.version
            )
            self.db.add(vendor)
            self.db.commit()
            self.db.refresh(vendor)
            return vendor

        # IDEMPOTENCY CHECK
        if payload.version <= vendor.version:
            return vendor  # ignore old or duplicate update

        # UPDATE
        vendor.name = payload.name
        vendor.version = payload.version
        self.db.commit()
        self.db.refresh(vendor)
        return vendor