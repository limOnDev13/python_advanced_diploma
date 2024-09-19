from typing import Dict, List, Tuple

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.queries import get_images_by_ids

BASE_ROUTE: str = "/api/tweets?api_key={api_key}"


@pytest.mark.asyncio
async def test_create_new_tweet_without_images(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Testing sending multiple tweets without images"""
    user_id, api_key = user_data
    new_tweet: Dict = {"tweet_data": "test_tweet_text"}
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=new_tweet)
    assert response.status_code == 201
    tweet_id = response.json()["tweet_id"]
    second_response = await client.post(
        BASE_ROUTE.format(api_key=api_key), json=new_tweet
    )
    assert second_response.status_code == 201
    assert tweet_id + 1 == second_response.json()["tweet_id"]


@pytest.mark.asyncio
async def test_invalid_tweet_form(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Negative testing of sending an invalid tweet form"""
    _, api_key = user_data
    invalid_tweet: Dict = {"invalid_field": "smth"}
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=invalid_tweet)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tweet_with_invalid_api_key(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Negative testing of sending tweet with invalid api_key"""
    user_id, _ = user_data
    invalid_api_key = "invalid_api_key"
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(
        BASE_ROUTE.format(api_key=invalid_api_key), json=new_tweet
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_tweet_with_images(
    client: AsyncClient,
    db_session: AsyncSession,
    user_data: Tuple[int, str],
    images_ids: List[int],
) -> None:
    """Testing sending tweet with images ids"""
    user_id, api_key = user_data

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=new_tweet)
    assert response.status_code == 201

    # check images - image.tweet_id must be equal tweet id
    images = await get_images_by_ids(db_session, images_ids)
    for image in images:
        assert response.json()["tweet_id"] == image.tweet_id


@pytest.mark.asyncio
async def test_create_tweet_with_non_existent_images(
    client: AsyncClient,
    db_session: AsyncSession,
    user_data: Tuple[int, str],
    images_ids: List[int],
) -> None:
    """Negative testing sending tweet with images ids that are not in the database"""
    user_id, api_key = user_data

    max_image_id: int = 0 if not images_ids else max(images_ids)
    images_ids_not_in_db: List[int] = [max_image_id + i for i in range(3)]

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids_not_in_db,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=new_tweet)
    assert response.status_code == 403

    # check - create tweet with existing and non-existing images
    images_ids_not_in_db.extend(images_ids)
    # create tweet
    second_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids_not_in_db,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=second_tweet)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_tweet_with_someone_else_images(
    client: AsyncClient,
    db_session: AsyncSession,
    user_data: Tuple[int, str],
    images_ids: List[int],
    image_id: int,
) -> None:
    """Negative testing sending tweet with images ids that relate other tweet"""
    user_id, api_key = user_data

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "tweet_media_ids": images_ids,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=new_tweet)
    assert response.status_code == 201

    # create second tweet with same images_ids
    second_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "tweet_media_ids": images_ids,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=second_tweet)
    assert response.status_code == 403

    # create third tweet with same images and new image
    images_ids.append(image_id)
    # create tweet
    third_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "tweet_media_ids": images_ids,
    }
    response = await client.post(BASE_ROUTE.format(api_key=api_key), json=third_tweet)
    assert response.status_code == 403
