from contextlib import asynccontextmanager

from fastapi import FastAPI

from schemas.schemas import Tweet
from database.database import engine, Base, Session


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


async def get_session():
    session = Session()
    try:
        yield session
    finally:
        await session.close()


app = FastAPI(lifespan=lifespan)


@app.post('/api/tweets')
async def create_new_tweet(api_key: str, tweet: Tweet):

    return {"result": "true", "tweet_id": 1}
