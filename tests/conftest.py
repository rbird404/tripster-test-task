import os
import pytest
import pytest_asyncio
from alembic.command import upgrade, downgrade

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from starlette.testclient import TestClient

from testcontainers.postgres import PostgresContainer
from alembic.config import Config as AlembicConfig
from src.config import Config
from src.database.dependency import get_async_session


@pytest.fixture(scope="session")
def init_postgres() -> PostgresContainer:
    with PostgresContainer() as postgres:
        os.environ["POSTGRES_HOST"] = postgres.get_container_host_ip()
        os.environ["POSTGRES_PORT"] = postgres.get_exposed_port(5432)
        os.environ["POSTGRES_DB"] = postgres.POSTGRES_DB
        os.environ["POSTGRES_USER"] = postgres.POSTGRES_USER
        os.environ["POSTGRES_PASSWORD"] = postgres.POSTGRES_PASSWORD
        yield postgres


@pytest.fixture(scope="session")
def postgres_url(init_postgres: PostgresContainer) -> str:
    return Config().get_db_url(async_=True)


@pytest.fixture
def migrations(postgres_url) -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_url)
    upgrade(alembic_cfg, "head")
    yield
    downgrade(alembic_cfg, "base")


@pytest_asyncio.fixture
async def db_session(migrations, postgres_url) -> AsyncSession:
    async_engine = create_async_engine(postgres_url, echo=False)

    async_session = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        autoflush=False,
    )
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
        finally:
            await session.close()


@pytest.fixture
def client(db_session) -> TestClient:
    from src.main import app

    async def test_session():
        try:
            yield db_session
        except Exception:
            await db_session.rollback()
        finally:
            await db_session.close()

    app.dependency_overrides[get_async_session] = test_session
    with TestClient(app) as client:
        yield client
