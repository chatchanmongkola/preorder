import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - ensures all models are registered on Base.metadata
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app


@pytest.fixture()
def db_session():
    # StaticPool keeps a single shared connection alive for the whole in-memory
    # SQLite DB; without it, each new connection from the pool would see a
    # brand-new (schema-less) database and every query would 500.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def _get_db_override():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _get_db_override
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
