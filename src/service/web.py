from contextlib import asynccontextmanager
from logging import getLogger
from typing import Optional

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import queries as q
from src.database.models import Base, Session, Tweet, engine, User
from src.service.exceptions import ForbiddenError, IdentificationError, NotFoundError

logger = getLogger("routes_logger")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Startup")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug("Before yield")
    yield
    logger.debug("After yield")
    # Shutdown
    logger.info("Shutdown")
    await engine.dispose()


async def get_session():
    logger.info("Getting session")
    session: AsyncSession = Session()
    # Check that the user table has rows
    if not await q.user_table_has_rows(session):
        logger.debug("Table User doesn't have any rows => add test user")
        await q.create_user(session, {"api_key": "test_api_key"})

    try:
        logger.debug("Before yield session")
        yield session
        logger.debug("After yield session")
    finally:
        await session.close()


async def check_api_key(
    api_key: str, session: AsyncSession = Depends(get_session)
) -> User:
    """
    The function checks if the given api_key is in the database.
    :param api_key: The key is the user ID
    :param session: async session object
    :raise HTTPException: if api_key is not in database
    :return: user_id (int) if api_key is in the database
    :rtype: int
    """
    logger.info("Start checking api_key")
    user: Optional[User] = await q.get_user_by_api_key(session, api_key)

    if not user:
        logger.warning("api_key not exists")
        raise IdentificationError("api_key not exists")

    logger.debug("Identification is successful")
    return user


async def check_tweet_exists(
        tweet_id: int,
        session: AsyncSession = Depends(get_session)) -> Tweet:
    """Function checks that tweet_id exists"""
    tweet: Optional[Tweet] = await q.get_tweet_by_id(session, tweet_id)
    if not tweet:
        raise NotFoundError(f"tweet_id {tweet_id} not found")
    return tweet


async def check_tweet_relates_user(tweet: Tweet, user_id: int = Depends(check_api_key)) -> None:
    """check that tweet relates user_id"""
    if tweet.user_id != user_id:
        raise ForbiddenError(f"The tweet {tweet.user_id} does not belong to user {user_id}")
