from contextlib import asynccontextmanager
from logging import getLogger
from typing import Optional

from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi_exceptions.exceptions import AuthenticationFailed, NotFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import queries as q
from src.database.models import Base, Session, Tweet, engine

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


def json_response_with_error(exc: Exception, status_code: int = 400) -> JSONResponse:
    """
    The function returns a JsonResponse in case of an error
    :param exc: Exception
    :param status_code: HTTP code
    :return: JSONResponse
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "result": False,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
        },
    )


async def check_api_key(
    api_key: str, session: AsyncSession, response: Response
) -> int | JSONResponse:
    """
    The function checks if the given api_key is in the database.
    :param api_key: The key is the user ID
    :param session: session object
    :param response: object of the response
    :return: user_id (int) if api_key is in the database,
    otherwise JSONResponse with an identification error response
    :rtype: int | JSONResponse
    """
    user_id: Optional[int] = await q.get_user_id_by_api_key(session, api_key)
    if not user_id:
        logger.warning("api_key %s not exists", api_key)
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return json_response_with_error(
            AuthenticationFailed(f"api_key {api_key} not exists"), 401
        )
    return user_id


async def check_tweet_id(
    tweet_id: int, session: AsyncSession
) -> Optional[JSONResponse]:
    """Function check tweet_id"""
    tweet: Optional[Tweet] = await q.get_tweet_by_id(session, tweet_id)
    if not tweet:
        return json_response_with_error(NotFound(f"tweet_id {tweet_id} not found"), 404)
    return None
