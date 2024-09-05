from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import schemas
from database.database import engine, Base, Session
from database import queries as q


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Check that the user table has rows
    session: AsyncSession = Session()
    if not q.user_table_has_rows(session):
        await q.create_user(session, {"api_key": "test_api_key"})

    yield
    # Shutdown
    await engine.dispose()


async def get_session():
    session: AsyncSession = Session()
    try:
        yield session
    finally:
        await session.close()


app = FastAPI(lifespan=lifespan)


@app.post('/api/tweets')
async def create_new_tweet(api_key: str, tweet: schemas.Tweet,
                           session: AsyncSession = Depends(get_session)) -> JSONResponse:
    """
    The endpoint creates a new tweet
    :param api_key: the user's api_key. Needed for identification
    :type api_key: str
    :param tweet: tweet's data
    :type tweet: schemas.schemas.Tweet
    :param session: the session object for working with the database.
    Provided by the Depends dependency function
    :type session: AsyncSession
    :return: json response with tweet_id
    :rtype: JSONResponse
    """
    return JSONResponse(content={"result": "true", "tweet_id": 1},
                        status_code=status.HTTP_201_CREATED)
