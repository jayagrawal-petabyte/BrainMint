"""
Shared pytest fixtures for the BrainMint backend test suite.

Uses an in-memory SQLite database so tests are:
  - Fast (no PostgreSQL dependency)
  - Isolated (each test gets a fresh DB via transaction rollback)
  - Self-contained (no seeding required)

Anti-spam services (rate limiter, CAPTCHA) are mocked by default so tests
can focus on business logic without hitting external APIs or bumping limits.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch

from app.main import app
from app.api.deps import get_db
from app.models.base import Base
# Import all models so SQLAlchemy registers them before create_all
from app.models import Enquiry, Service, SiteSetting, FAQ, SocialLink, AdminUser  # noqa: F401
from app.core.security import get_password_hash, create_access_token


# ---------------------------------------------------------------------------
# Database setup – in-memory SQLite for tests
# ---------------------------------------------------------------------------
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Create all tables once per test session."""
    import app.core.database
    import app.services.email_service
    app.core.database.SessionLocal = TestingSessionLocal
    app.services.email_service.SessionLocal = TestingSessionLocal
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Session:
    """
    Provide a transactional DB session that rolls back after each test,
    keeping tests isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    """
    FastAPI TestClient with the real DB dependency overridden to use the
    test session, anti-spam services mocked, and pre-authenticated with an admin token.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Seed test admin user for admin-protected endpoints
    admin = db.query(AdminUser).filter(AdminUser.email == "admin@brainmint.com").first()
    if not admin:
        admin = AdminUser(
            email="admin@brainmint.com",
            hashed_password=get_password_hash("adminpassword123"),
            is_active=True
        )
        db.add(admin)
        db.commit()
    
    token = create_access_token(data={"sub": admin.email})

    # Bypass CAPTCHA and rate limiting for all tests by default
    with (
        patch("app.services.captcha_service.captcha_service.verify", return_value=None),
        patch("app.core.rate_limit.enquiry_limiter.check", return_value=None),
        patch("app.core.rate_limit.admin_enquiry_limiter.check", return_value=None),
    ):
        test_client = TestClient(app)
        test_client.headers = {**test_client.headers, "Authorization": f"Bearer {token}"}
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def client_no_mock(db: Session) -> TestClient:
    """
    TestClient WITHOUT mocked rate limiter / CAPTCHA.
    Use for tests that explicitly test anti-spam behaviour.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.services.captcha_service.captcha_service.verify", return_value=None):
        yield TestClient(app)

    app.dependency_overrides.clear()