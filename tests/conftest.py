from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.models import DB_URL, Base, User
from src.routes import create_app, get_session


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Start a test database session"""
    engine = create_async_engine(DB_URL)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session = Session()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield session
    await session.close()


@pytest.fixture(scope="function")
def test_app(db_session: AsyncSession) -> Generator[FastAPI, None, None]:
    """Create a test_app with overridden dependencies"""
    _app: FastAPI = create_app()
    _app.dependency_overrides[get_session] = lambda: db_session
    yield _app
    _app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a http client"""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://localhost:8000"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def user_data(db_session: AsyncSession):
    async with db_session.begin():
        user: User = User(api_key="test_api_key")
        db_session.add(user)
        await db_session.commit()
    yield user.id, "test_api_key"
