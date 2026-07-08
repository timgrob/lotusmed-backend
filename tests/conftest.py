from collections.abc import AsyncGenerator

import pytest
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.db.database import Base, get_session
from src.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    # Fresh in-memory DB per test; StaticPool keeps the single connection alive
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    import src.models.user  # noqa: F401  (register tables on Base.metadata)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    TestingSessionLocal = async_sessionmaker(
        engine, autoflush=False, expire_on_commit=False
    )
    async with TestingSessionLocal() as db_session:
        yield db_session


@pytest.fixture
async def client(engine: AsyncEngine) -> AsyncGenerator[AsyncClient, None]:
    TestingSessionLocal = async_sessionmaker(
        engine, autoflush=False, expire_on_commit=False
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    # ASGITransport calls the app in-process; lifespan is not run, so tests
    # never touch the real dev DB
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
