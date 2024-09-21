from contextlib import asynccontextmanager
from logging import getLogger
from typing import Optional

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.config import Config, load_config
from src.database import queries as q
from src.database.models import Base, Session, Tweet, User, engine
from src.service.exceptions import ForbiddenError, IdentificationError, NotFoundError

logger = getLogger("routes_logger")

config: Config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The function creates a database connection session.
    If the DROP_ALL environment variable is equal 1,
    then the entire database will be dropped before creation (only during development)
    """
    # Startup
    logger.info("Startup")
    async with engine.begin() as conn:
        if config.debug:
            logger.debug("drop all")
            await conn.run_sync(Base.metadata.drop_all)
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

    if config.debug:
        # Check count users in db
        num_users: Optional[int] = await q.count_users(session)
        logger.debug("There are %d users in the table", num_users)

        # There must be at least two users in the table
        if num_users is not None:  # mypy
            for num in range(num_users + 1, 3):
                new_user: User = await q.create_user(
                    session, {"api_key": f"api_key_{num}", "name": f"name_{num}"}
                )
                logger.debug(
                    "Add user with id %d and api_key api_key_%d", new_user.id, num
                )

        # add user with api-key=test
        new_user: User = await q.create_user(
            session, {"api_key": "test", "name": "test"}
        )
        logger.debug("Add user with id %d and api_key %s", new_user.id, "test")

    try:
        logger.debug("Before yield session")
        yield session
        logger.debug("After yield session")
    finally:
        await session.close()


async def check_api_key(api_key: str, session: AsyncSession) -> User:
    """
    The function checks if the given api_key is in the database.
    :param api_key: The key is the user ID
    :param session: async session object
    :raise HTTPException: if api_key is not in database
    :return: user if api_key is in the database
    :rtype: User
    """
    logger.info("Start checking api_key")
    user: Optional[User] = await q.get_user_by_api_key(session, api_key)

    if not user:
        logger.warning("api_key not exists")
        raise IdentificationError("api_key not exists")

    logger.info("Identification is successful")
    return user


async def check_users_exists(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> User:
    """
    The function checks that user with user_id exists.
    :param user_id: the user ID
    :param session: async session object
    :raise HTTPException: if user_id is not in database
    :return: user if user_id is in the database
    :rtype: User
    """
    logger.info("Start checking user_id")
    user: Optional[User] = await q.get_user_by_id(session, user_id)

    if not user:
        logger.warning("user_id %d not exists", user_id)
        raise NotFoundError(f"user_id {user_id} not exists")

    logger.debug("User was found")
    return user


async def check_tweet_exists(
    tweet_id: int, session: AsyncSession = Depends(get_session)
) -> Tweet:
    """Function checks that tweet_id exists"""
    tweet: Optional[Tweet] = await q.get_tweet_by_id(session, tweet_id)
    if not tweet:
        raise NotFoundError(f"tweet_id {tweet_id} not found")
    return tweet


async def check_tweet_relates_user(
    tweet: Tweet, user_id: int = Depends(check_api_key)
) -> None:
    """check that tweet relates user_id"""
    if tweet.user_id != user_id:
        raise ForbiddenError(
            f"The tweet {tweet.user_id} does not belong to user {user_id}"
        )
