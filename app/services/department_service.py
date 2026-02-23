from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department_schema import DepartmentCreate

class DepartmentService:

    def __init__(self, db: Session):
        self.db = db

    def upsert_department(self, payload: DepartmentCreate) -> Department:
        department = (
            self.db.query(Department)
            .filter(Department.external_id == payload.external_id)
            .first()
        )

        if not department:
            department = Department(
                external_id=payload.external_id,
                name=payload.name,
                version=payload.version
            )
            self.db.add(department)
            self.db.commit()
            self.db.refresh(department)
            return department

        if payload.version <= department.version:
            return department

        department.name = payload.name
        department.version = payload.version

        self.db.commit()
        self.db.refresh(department)
        return department