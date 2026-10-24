import time
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.crud.service import service_crud
from app.crud.content import content_crud

class ContentService:
    def __init__(self, cache_ttl: int = 120):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = cache_ttl

    def get_cached(self, key: str) -> Optional[Any]:
        item = self._cache.get(key)
        if item and (time.time() - item["timestamp"] < self.ttl):
            return item["data"]
        return None

    def set_cached(self, key: str, data: Any):
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    def invalidate(self, prefix: Optional[str] = None):
        if not prefix:
            self._cache.clear()
        else:
            self._cache = {k: v for k, v in self._cache.items() if not k.startswith(prefix)}

    def get_public_services(self, db: Session):
        cache_key = "services:active"
        cached = self.get_cached(cache_key)
        if cached is not None:
            return cached
        services = service_crud.get_active_services(db)
        self.set_cached(cache_key, services)
        return services

    def get_public_service_by_slug(self, db: Session, slug: str):
        cache_key = f"service:{slug}"
        cached = self.get_cached(cache_key)
        if cached is not None:
            return cached
        service = service_crud.get_by_slug(db, slug)
        if service:
            self.set_cached(cache_key, service)
        return service

    def get_public_setting(self, db: Session, key: str):
        cache_key = f"setting:{key}"
        cached = self.get_cached(cache_key)
        if cached is not None:
            return cached
        setting = content_crud.get_setting(db, key)
        data = setting.value if setting else {}
        self.set_cached(cache_key, data)
        return data

content_service = ContentService(cache_ttl=120)