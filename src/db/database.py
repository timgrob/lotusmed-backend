from sqlalchemy import create_engine, MetaData, StaticPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import get_settings

settings = get_settings()

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.APP_ENV != "prod",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_test_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables() -> None:
    Base.metadata.create_all(engine)
