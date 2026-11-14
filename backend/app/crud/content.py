from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.content import SiteSetting, FAQ, SocialLink
from app.schemas.content import FAQCreate, FAQUpdate, SocialLinkCreate, SocialLinkUpdate

class CRUDContent:
    def get_setting(self, db: Session, key: str) -> Optional[SiteSetting]:
        return db.query(SiteSetting).filter(SiteSetting.key == key).first()

    def set_setting(self, db: Session, key: str, value: Dict[str, Any], description: Optional[str] = None) -> SiteSetting:
        setting = self.get_setting(db, key)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SiteSetting(key=key, value=value, description=description)
            db.add(setting)
        db.commit()
        db.refresh(setting)
        return setting

    # FAQs
    def get_published_faqs(self, db: Session, category: Optional[str] = None) -> List[FAQ]:
        query = db.query(FAQ).filter(FAQ.is_published == True)
        if category:
            query = query.filter(FAQ.category == category)
        return query.order_by(FAQ.display_order.asc()).all()

    def get_all_faqs(self, db: Session) -> List[FAQ]:
        return db.query(FAQ).order_by(FAQ.display_order.asc()).all()

    def create_faq(self, db: Session, obj_in: FAQCreate) -> FAQ:
        faq = FAQ(**obj_in.model_dump())
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq

    def update_faq(self, db: Session, faq: FAQ, obj_in: FAQUpdate) -> FAQ:
        data = obj_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(faq, field, value)
        db.commit()
        db.refresh(faq)
        return faq

    def delete_faq(self, db: Session, faq_id: int) -> Optional[FAQ]:
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if faq:
            db.delete(faq)
            db.commit()
        return faq

    # Social Links
    def get_active_social_links(self, db: Session) -> List[SocialLink]:
        return db.query(SocialLink).filter(SocialLink.is_active == True).order_by(SocialLink.display_order.asc()).all()

    def get_all_social_links(self, db: Session) -> List[SocialLink]:
        return db.query(SocialLink).order_by(SocialLink.display_order.asc()).all()

    def create_social_link(self, db: Session, obj_in: SocialLinkCreate) -> SocialLink:
        social = SocialLink(**obj_in.model_dump())
        db.add(social)
        db.commit()
        db.refresh(social)
        return social

    def update_social_link(self, db: Session, social: SocialLink, obj_in: SocialLinkUpdate) -> SocialLink:
        data = obj_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(social, field, value)
        db.commit()
        db.refresh(social)
        return social

    def delete_social_link(self, db: Session, link_id: int) -> Optional[SocialLink]:
        link = db.query(SocialLink).filter(SocialLink.id == link_id).first()
        if link:
            db.delete(link)
            db.commit()
        return link

content_crud = CRUDContent()