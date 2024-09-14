from typing import Dict, Tuple

import pytest


@pytest.mark.asyncio
async def test_delete_tweet(client, user_data: Tuple[int, str]) -> None:
    """Testing deleting tweet"""
    # create tweet
    user_id, api_key = user_data
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(f"/api/tweets?api_key={api_key}", json=new_tweet)
    assert response.status_code == 201
    tweet_id: int = response.json()["tweet_id"]

    # delete this tweet
    response = await client.delete(f"/api/tweets/{tweet_id}?api_key={api_key}")
    assert response.status_code == 200
