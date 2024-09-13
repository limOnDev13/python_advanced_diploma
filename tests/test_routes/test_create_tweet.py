from typing import Dict, List, Tuple

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.queries import get_all_images_ids, get_images_by_ids
from tests.test_routes.test_upload_image import BASE_ROUTE, TEST_IMAGE_PATH


@pytest.mark.asyncio
async def test_create_new_tweet(client, user_data: Tuple[int, str]) -> None:
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
async def test_invalid_tweet_form(client, user_data: Tuple[int, str]) -> None:
    """Negative testing of sending an invalid tweet form"""
    _, api_key = user_data
    invalid_tweet: Dict = {"invalid_field": "smth"}
    response = await client.post(f"/api/tweets?api_key={api_key}", json=invalid_tweet)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_api_key(client, user_data: Tuple[int, str]) -> None:
    """Negative testing of sending tweet with invalid api_key"""
    user_id, _ = user_data
    invalid_api_key = "invalid_api_key"
    new_tweet: Dict = {"tweet_data": "test_tweet_text", "user_id": user_id}
    response = await client.post(
        f"/api/tweets?api_key={invalid_api_key}", json=new_tweet
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_tweet_with_images(
    client, db_session: AsyncSession, user_data: Tuple[int, str]
) -> None:
    """Testing sending tweet with images ids"""
    user_id, api_key = user_data

    # Send some images
    images_ids: List[int] = list()
    for _ in range(3):
        response = await client.post(
            BASE_ROUTE.format(api_key),
            files={
                "image": (
                    "test.jpg",
                    open(TEST_IMAGE_PATH, "rb"),
                    "multipart/form-data",
                )
            },
        )
        images_ids.append(response.json()["image_id"])

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=new_tweet)
    assert response.status_code == 201

    # check images - image.tweet_id must be equal tweet id
    images = await get_images_by_ids(db_session, images_ids)
    for image in images:
        assert response.json()["tweet_id"] == image.tweet_id


@pytest.mark.asyncio
async def test_create_tweet_with_non_existent_images(
    client, db_session: AsyncSession, user_data: Tuple[int, str]
) -> None:
    """Negative testing sending tweet with images ids that are not in the database"""
    user_id, api_key = user_data

    # get images ids in db
    images_ids: List[int] = await get_all_images_ids(db_session)
    max_image_id: int = 0 if not images_ids else max(images_ids)
    images_ids_not_in_db: List[int] = [max_image_id + i for i in range(3)]

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids_not_in_db,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=new_tweet)
    assert response.status_code == 403

    # check - create tweet with existing and non-existing images
    # send new image
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
    )
    images_ids_not_in_db.append(response.json()["image_id"])
    # create tweet
    second_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids_not_in_db,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=second_tweet)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_tweet_with_someone_else_images(
    client, db_session: AsyncSession, user_data: Tuple[int, str]
) -> None:
    """Negative testing sending tweet with images ids that relate other tweet"""
    user_id, api_key = user_data

    # Send some images
    images_ids: List[int] = list()
    for _ in range(3):
        response = await client.post(
            BASE_ROUTE.format(api_key),
            files={
                "image": (
                    "test.jpg",
                    open(TEST_IMAGE_PATH, "rb"),
                    "multipart/form-data",
                )
            },
        )
        images_ids.append(response.json()["image_id"])

    # create tweet with images_ids
    new_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=new_tweet)
    assert response.status_code == 201

    # create second tweet with same images_ids
    second_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=second_tweet)
    assert response.status_code == 403

    # create third tweet with same images and new images
    # send new image
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
    )
    images_ids.append(response.json()["image_id"])
    # create tweet
    third_tweet: Dict = {
        "tweet_data": "test_tweet_text",
        "user_id": user_id,
        "tweet_media_ids": images_ids,
    }
    response = await client.post(f"/api/tweets?api_key={api_key}", json=third_tweet)
    assert response.status_code == 403
