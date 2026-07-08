from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.database import Base, get_session
from src.main import app


@pytest.fixture
def engine():
    # Fresh in-memory DB per test; StaticPool keeps the single connection alive
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    import src.models.user  # noqa: F401  (register tables on Base.metadata)

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with TestingSessionLocal() as db_session:
        yield db_session


@pytest.fixture
def client(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_session():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    # No context manager: skips lifespan, so tests never touch the real dev DB
    yield TestClient(app)
    app.dependency_overrides.clear()
