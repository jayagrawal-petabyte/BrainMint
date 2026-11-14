from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate

class CRUDService:
    def get(self, db: Session, service_id: int) -> Optional[Service]:
        return db.query(Service).filter(Service.id == service_id).first()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Service]:
        return db.query(Service).filter(Service.slug == slug, Service.is_active == True).first()

    def get_active_services(self, db: Session) -> List[Service]:
        return db.query(Service).filter(Service.is_active == True).order_by(Service.display_order.asc()).all()

    def get_all(self, db: Session) -> List[Service]:
        return db.query(Service).order_by(Service.display_order.asc()).all()

    def create(self, db: Session, obj_in: ServiceCreate) -> Service:
        db_obj = Service(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Service, obj_in: ServiceUpdate) -> Service:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, service_id: int) -> Optional[Service]:
        obj = db.query(Service).filter(Service.id == service_id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

service_crud = CRUDService()