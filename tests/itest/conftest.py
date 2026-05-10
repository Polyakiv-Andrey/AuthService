from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.db.session import get_db
from src.main import app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def setup_database(postgres_container):
    raw_url = postgres_container.get_connection_url()
    db_url = "postgresql+asyncpg://" + raw_url.split("://")[1]

    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    ini_path = str(project_root / "alembic.ini")
    script_location = str(project_root / "migrations")

    alembic_cfg = Config(ini_path)
    alembic_cfg.set_main_option("script_location", script_location)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(alembic_cfg, "head")

    return db_url


@pytest.fixture
async def async_client(setup_database):
    engine = create_async_engine(setup_database)
    TestingSessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def db_session(setup_database):
    engine = create_async_engine(setup_database)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
    await engine.dispose()
