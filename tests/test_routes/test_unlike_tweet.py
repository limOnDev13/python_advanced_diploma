from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/tweets/{tweet_id}/likes?api_key={api_key}"


@pytest.mark.asyncio
async def test_unlike_tweet(
    client: AsyncClient, user_data: Tuple[int, str], tweet_id_with_like: int
) -> None:
    """Testing unliking tweets"""
    user_id, api_key = user_data

    # unlike a tweet
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_like, api_key=api_key)
    )
    assert response.status_code == 200
    # unlike this tweet again
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_like, api_key=api_key)
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unlike_tweet_with_invalid_api_key(
    client: AsyncClient, tweet_id_with_like: int
) -> None:
    """Testing unliking tweet with invalid api_key"""
    api_key: str = "invalid_api_key"

    # like tweet with images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_like, api_key=api_key)
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unlike_not_existing_tweet(
    client: AsyncClient, user_data: Tuple[int, int]
) -> None:
    """Negative test of unliking not existing tweet"""
    _, api_key = user_data
    invalid_tweet_id: int = 100

    # unlike tweet with images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=invalid_tweet_id, api_key=api_key)
    )
    assert response.status_code == 404
