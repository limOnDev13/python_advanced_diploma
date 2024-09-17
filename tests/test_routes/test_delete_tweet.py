from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/tweets/{tweet_id}?api_key={api_key}"


@pytest.mark.asyncio
async def test_delete_tweet_without_images(
    client: AsyncClient, user_data: Tuple[int, str], tweet_id_without_img: int
) -> None:
    """Testing deleting tweet without images"""
    # create tweet
    user_id, api_key = user_data

    # delete this tweet
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img, api_key=api_key)
    )
    assert response.status_code == 200

    # if you try to delete the same tweet, there must be a 404 error
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img, api_key=api_key)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tweet_with_images(
    client: AsyncClient, user_data: Tuple[int, str], tweet_id_with_images: int
) -> None:
    """Testing deleting tweet with images"""
    user_id, api_key = user_data
    # delete tweet
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images, api_key=api_key)
    )
    assert response.status_code == 200

    # if you try to delete the same tweet, there must be a 404 error
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images, api_key=api_key)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tweet_with_invalid_api_key(
    client: AsyncClient, user_data, tweet_id_with_images: int, tweet_id_without_img: int
) -> None:
    """Negative testing deleting tweet with invalid api_key"""
    user_id, _ = user_data
    api_key: str = "invalid_api_key"
    # try deleting existing tweet with images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images, api_key=api_key)
    )
    assert response.status_code == 401

    # try deleting existing tweet without images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img, api_key=api_key)
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_not_existing_tweet(client: AsyncClient, user_data) -> None:
    """Negative testing deleting not existing tweet"""
    user_id, api_key = user_data

    # before each test, the database is reset and there are no tweets in it
    not_existing_tweet_id: int = 123
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=not_existing_tweet_id, api_key=api_key)
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_not_user_tweet(
    client: AsyncClient,
    other_user_data,
    tweet_id_with_images: int,
    tweet_id_without_img: int,
) -> None:
    """A negative test of deleting a tweet that does not belong to this user"""
    _, other_api_key = other_user_data

    # try deleting existing tweet with images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_with_images, api_key=other_api_key)
    )
    assert response.status_code == 403

    # try deleting existing tweet without images
    response = await client.delete(
        BASE_ROUTE.format(tweet_id=tweet_id_without_img, api_key=other_api_key)
    )
    assert response.status_code == 403
