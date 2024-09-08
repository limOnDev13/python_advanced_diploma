from typing import Dict

import pytest


@pytest.mark.asyncio
async def test_create_new_tweet(client, user_data: tuple[int, str]) -> None:
    """Testing sending multiple tweets"""
    user_id, api_key = user_data
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(f"/api/tweets?api_key={api_key}", json=new_tweet)
    assert response.status_code == 201
    tweet_id = response.json()["tweet_id"]
    second_response = await client.post(
        f"/api/tweets?api_key={api_key}", json=new_tweet
    )
    assert second_response.status_code == 201
    assert tweet_id + 1 == second_response.json()["tweet_id"]


@pytest.mark.asyncio
async def test_invalid_tweet_form(client, user_data: tuple[int, str]) -> None:
    """Negative testing of sending an invalid tweet form"""
    _, api_key = user_data
    invalid_tweet: Dict = {"invalid_field": "smth"}
    response = await client.post(f"/api/tweets?api_key={api_key}", json=invalid_tweet)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_api_key(client, user_data: tuple[int, str]) -> None:
    """Negative testing of sending tweet with invalid api_key"""
    user_id, _ = user_data
    invalid_api_key = "invalid_api_key"
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(
        f"/api/tweets?api_key={invalid_api_key}", json=new_tweet
    )
    assert response.status_code == 401
