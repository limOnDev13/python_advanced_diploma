from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/tweets/{tweet_id}/likes"


@pytest.mark.asyncio
async def test_like_tweet(
    client: AsyncClient,
    user_data: Tuple[int, str],
    tweet_id_with_images: int,
    tweet_id_without_img: int,
) -> None:
    """Testing liking tweets"""
    user_id, api_key = user_data

    # like tweet with images
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images), headers={"api-key": api_key}
    )
    assert response.status_code == 200
    # try like same tweet
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images), headers={"api-key": api_key}
    )
    assert response.status_code == 400
    # like tweet without images
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img), headers={"api-key": api_key}
    )
    assert response.status_code == 200
    # try like same tweet
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img), headers={"api-key": api_key}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_like_someone_else_tweet(
    client: AsyncClient,
    user_data: Tuple[int, str],
    other_user_data: Tuple[int, int],
    tweet_id_with_images: int,
) -> None:
    """Testing when someone else liking tweet"""
    _, api_key = user_data
    _, other_api_key = other_user_data

    # owner likes tweet
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images), headers={"api-key": api_key}
    )
    assert response.status_code == 200
    # someone else likes tweet
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images),
        headers={"api-key": other_api_key},
    )
    assert response.status_code == 200
    # someone else likes same tweet
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images),
        headers={"api-key": other_api_key},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_like_tweet_with_invalid_api_key(
    client: AsyncClient, tweet_id_with_images: int, tweet_id_without_img: int
) -> None:
    """Testing liking tweet with invalid api_key"""
    api_key: str = "invalid_api_key"

    # like tweet with images
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images), headers={"api-key": api_key}
    )
    assert response.status_code == 401

    # like tweet without images
    response = await client.post(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img), headers={"api-key": api_key}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_like_not_existing_tweet(
    client: AsyncClient, user_data: Tuple[int, int]
) -> None:
    """Negative test of liking not existing tweet"""
    _, api_key = user_data
    invalid_tweet_id: int = 100

    # like tweet with images
    response = await client.post(
        BASE_ROUTE.format(tweet_id=invalid_tweet_id), headers={"api-key": api_key}
    )
    assert response.status_code == 404
