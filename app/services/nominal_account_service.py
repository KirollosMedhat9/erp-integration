from sqlalchemy.orm import Session
from app.models.nominal_account import NominalAccount
from app.schemas.nominal_account_schema import NominalAccountCreate

class NominalAccountService:

    def __init__(self, db: Session):
        self.db = db

    def upsert_nominal_account(self, payload: NominalAccountCreate) -> NominalAccount:
        account = (
            self.db.query(NominalAccount)
            .filter(NominalAccount.external_id == payload.external_id)
            .first()
        )

        if not account:
            account = NominalAccount(
                external_id=payload.external_id,
                name=payload.name,
                version=payload.version
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            return account

        if payload.version <= account.version:
            return account

        account.name = payload.name
        account.version = payload.version

        self.db.commit()
        self.db.refresh(account)
        return account