import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import async_session
from src.main import app
from src.publications.models import Publication
from src.users.models import User


@pytest.fixture(autouse=True, scope="session")
def run_migrations() -> None:
    import os

    print("running migrations..")
    os.system("alembic upgrade head")


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "9000"
    scope = {"client": (host, port)}

    async with TestClient(app, scope=scope) as client:
        yield client


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def credentials(client: TestClient) -> str:
    resp = await client.post(
        "/auth/token",
        json={
            "username": "test_user",
            "password": "123Aa!",
        },
    )

    resp_json = resp.json()
    access_token = resp_json["details"]["access_token"]
    return f"Bearer {access_token}"


@pytest_asyncio.fixture
async def publication(db_session: AsyncSession) -> Publication:
    user = await db_session.scalar(
        select(User).where(User.username == "test_user")
    )
    publication = Publication(content="test", creator_id=user.id)
    db_session.add(publication)
    await db_session.commit()
    return publication
