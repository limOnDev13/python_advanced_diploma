import os
from typing import AsyncGenerator, Callable, Dict, Generator, List, Tuple

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.database.queries as q
from src.api.routes import create_app
from src.config.config import load_config
from src.database.models import Base
from src.service.images import delete_images_by_ids
from src.service.web import get_session

db_config = load_config()
DB_URL: str = db_config.db.url


@pytest_asyncio.fixture(scope="function", autouse=True)
async def engine():
    engine = create_async_engine(DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[Callable, None]:
    """Start a test database session"""
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session: AsyncSession = Session()

    # add 2 users
    await q.create_user(session, {"api_key": "test_api_key", "name": "test"})
    await q.create_user(session, {"api_key": "other_test_api_key", "name": "test"})

    async def overrides_get_session(request: Request):
        request.state.session = session
        yield

    yield overrides_get_session
    await session.close()


@pytest.fixture(scope="function")
def test_app(db_session) -> Generator[FastAPI, None, None]:
    """Create a test_app with overridden dependencies"""
    _app: FastAPI = create_app()
    _app.dependency_overrides[get_session] = db_session
    yield _app
    _app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a http client"""
    os.environ["ENV"] = "test"
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://localhost:8000"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def user_data() -> AsyncGenerator[Tuple[int, str], None]:
    """Fixture. Returns id and api_key of test user"""
    yield 1, "test_api_key"


@pytest_asyncio.fixture(scope="function")
async def other_user_data(
    db_session: AsyncSession,
) -> AsyncGenerator[Tuple[int, str], None]:
    """Fixture. Returns id and api_key of second test user"""
    yield 2, "other_test_api_key"


@pytest_asyncio.fixture(scope="function")
async def tweet_id_without_img(
    client: AsyncClient, user_data
) -> AsyncGenerator[int, None]:
    """Fixture. Returns id of tweet without images"""
    user_id, api_key = user_data
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(
        "/api/tweets", json=new_tweet, headers={"api-key": api_key}
    )
    yield response.json()["tweet_id"]


@pytest.fixture(scope="function")
def images_path() -> Generator[str, None, None]:
    """Fixture. Returns path to images"""
    yield os.path.join(os.path.abspath("."), "client", "static", "images")


@pytest_asyncio.fixture(scope="function")
async def image_id(client: AsyncClient, user_data) -> AsyncGenerator[int, None]:
    """Fixture. Returns id of uploaded image"""
    _, api_key = user_data
    response = await client.post(
        "/api/medias",
        files={
            "image": (
                "test.jpg",
                open("tests/test_routes/images/test.jpg", "rb"),
                "multipart/form-data",
            )
        },
        headers={"api-key": api_key},
    )
    image_id = response.json()["media_id"]
    yield image_id

    # after the tests, need to delete the created image
    await delete_images_by_ids([image_id])


@pytest_asyncio.fixture(scope="function")
async def images_ids(
    client: AsyncClient, user_data, images_path: str
) -> AsyncGenerator[List[int], None]:
    """Fixture. Returns list of ids of uploaded images"""
    user_id, api_key = user_data

    # Send some images
    images_ids: List[int] = list()
    for _ in range(3):
        response = await client.post(
            "/api/medias",
            files={
                "image": (
                    "test.jpg",
                    open("tests/test_routes/images/test.jpg", "rb"),
                    "multipart/form-data",
                )
            },
            headers={"api-key": api_key},
        )
        images_ids.append(response.json()["media_id"])
    yield images_ids

    # after the tests, need to delete the created images
    await delete_images_by_ids(images_ids)


@pytest_asyncio.fixture(scope="function")
async def tweet_id_with_images(
    client: AsyncClient, user_data, images_ids: List[int]
) -> AsyncGenerator[int, None]:
    """Fixture. Returns id of tweet with images"""
    user_id, api_key = user_data
    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(
        "/api/tweets", json=new_tweet, headers={"api-key": api_key}
    )

    yield response.json()["tweet_id"]

    # after the tests, need to delete the created images
    await delete_images_by_ids(images_ids)


@pytest_asyncio.fixture(scope="function")
async def tweet_id_with_like(
    client: AsyncClient, user_data: Tuple[int, str], tweet_id_with_images: int
) -> AsyncGenerator[int, None]:
    """Fixture. Returns id of the tweet with like from user_data"""
    _, api_key = user_data
    # like this tweet
    await client.post(
        f"/api/tweets/{tweet_id_with_images}/likes", headers={"api-key": api_key}
    )

    yield tweet_id_with_images


@pytest_asyncio.fixture(scope="function")
async def follower_api_key_and_author_id(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> AsyncGenerator[Tuple[str, int], None]:
    """Fixture. Returns follower api_key and author id"""
    _, follower_api_key = user_data
    author_id, _ = other_user_data
    # follow author
    await client.post(
        f"/api/users/{author_id}/follow", headers={"api-key": follower_api_key}
    )
    yield follower_api_key, author_id
