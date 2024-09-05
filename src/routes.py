from fastapi import FastAPI

from schemas.schemas import Tweet


app = FastAPI()


@app.post('/api/tweets')
async def create_new_tweet(api_key: str, tweet: Tweet):
    return {"result": "true", "tweet_id": 1}
