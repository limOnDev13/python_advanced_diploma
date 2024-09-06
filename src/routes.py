from contextlib import asynccontextmanager
from typing import Optional
from logging import getLogger
from logging.config import dictConfig

from fastapi import FastAPI, status, Depends, Response
from fastapi.responses import JSONResponse
from fastapi_exceptions.exceptions import AuthenticationFailed
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from schemas import schemas
from database.models import engine, Base, Session
from database import queries as q
from database import models
from config.log_config import dict_config


dictConfig(dict_config)
logger = getLogger('routes_logger')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info('Startup')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug('Before yield')
    yield
    logger.debug('After yield')
    # Shutdown
    logger.info('Shutdown')
    await engine.dispose()


async def get_session():
    logger.info('Getting session')
    session: AsyncSession = Session()
    # Check that the user table has rows
    if not await q.user_table_has_rows(session):
        logger.debug("Table User doesn't have any rows => add test user")
        await q.create_user(session, {"api_key": "test_api_key"})

    try:
        logger.debug('Before yield session')
        yield session
        logger.debug('After yield session')
    finally:
        await session.close()


app = FastAPI(lifespan=lifespan)


@app.post(
    '/api/tweets',
    status_code=201,
    responses={
        401: {"description": "api_key not exists",
              "content": {
                  "application/json": {
                      "example": {"result": False,
                                  "error_type": "AuthenticationFailed",
                                  "error_message": "api_key <api_key> not exists"
                                  }
                  }
              }
        },
        201: {"description": "Tweet was created",
              "content": {
                  "application/json": {
                      "example": {"result": True, "tweet_id": 1}
                  }
              }
        }
    }
)
async def create_new_tweet(api_key: str, tweet: schemas.Tweet,
                           response: Response,
                           session: AsyncSession = Depends(get_session)):
    """
    The endpoint creates a new tweet.
    """
    logger.info('Start creating a new tweet')
    user_id: Optional[models.User] = await q.get_user_id_by_api_key(session, api_key)
    if not user_id:
        logger.warning(f'api_key {api_key} not exists')
        response.status_code = status.HTTP_403_FORBIDDEN
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"result": False,
                     "error_type": "AuthenticationFailed",
                     "error_message": f"api_key {api_key} not exists"})

    logger.debug('api_key exists')
    tweet_id: int = await q.create_tweet(session, user_id[0], tweet.model_dump())
    logger.debug(f'Tweet was created, tweet_id={tweet_id}')
    response.status_code = status.HTTP_201_CREATED
    return {"result": "true", "tweet_id": tweet_id}


if __name__ == '__main__':
    uvicorn.run(app)
