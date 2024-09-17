from contextlib import asynccontextmanager
from logging import getLogger
from typing import Optional

from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import queries as q
from src.database.models import Base, Session, Tweet, engine
from src.service.exceptions import IdentificationError, NotFoundError, ForbiddenError

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


async def check_api_key(api_key: str, session: AsyncSession = Depends(get_session)) -> int:
    """
    The function checks if the given api_key is in the database.
    :param api_key: The key is the user ID
    :param session: async session object
    :raise HTTPException: if api_key is not in database
    :return: user_id (int) if api_key is in the database
    :rtype: int
    """
    logger.info("Start checking api_key")
    user_id: Optional[int] = await q.get_user_id_by_api_key(session, api_key)

    if not user_id:
        logger.warning("api_key not exists")
        raise IdentificationError("api_key not exists")

    logger.debug("Identification is successful")
    return user_id


async def check_tweet_id(
    tweet_id: int, user_id: int, session: AsyncSession
) -> None:
    """Function check tweet_id"""
    # Check that tweet_id exists
    tweet: Optional[Tweet] = await q.get_tweet_by_id(session, tweet_id)
    if not tweet:
        raise NotFoundError(f"tweet_id {tweet_id} not found")

    # check that tweet relates user_id
    if tweet.user_id != user_id:
        raise ForbiddenError(f"The tweet {tweet_id} does not belong to user {user_id}")
