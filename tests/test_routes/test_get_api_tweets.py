from typing import Any, Dict, List, Tuple

import pytest
from httpx import AsyncClient

from src.service.images import delete_images_by_ids

BASE_ROUTE: str = "/api/tweets?api_key={api_key}"


@pytest.mark.asyncio
async def test_get_empty_list_of_tweets(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Testing getting an empty tweet feed"""
    user_id, api_key = user_data

    # create request
    response = await client.get(BASE_ROUTE.format(api_key=api_key))
    assert response.status_code == 200
    # check response json
    response_json: Dict[str, Any] = response.json()
    assert response_json["result"] is True
    assert "tweets" in response_json
    assert isinstance(response_json["tweets"], list)
    assert len(response_json["tweets"]) == 0


@pytest.mark.asyncio
async def test_get_list_of_tweets_without_images(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing getting tweet feed without images"""
    user_id, api_key = user_data
    other_user_id, other_api_key = other_user_data

    # 1) Subscribe one user to another
    response = await client.post(f"/api/users/{other_user_id}/follow?api_key={api_key}")
    assert response.status_code == 200

    # 2) Create three tweets from other user
    new_tweet: Dict = {"tweet_data": "test_tweet_text"}
    for _ in range(3):
        response = await client.post(
            f"/api/tweets?api_key={other_api_key}", json=new_tweet
        )
        assert response.status_code == 201

    # 3) Like twice 2, once 3 and don't like 1 tweets
    response = await client.post(f"/api/tweets/{2}/likes?api_key={api_key}")
    assert response.status_code == 200
    response = await client.post(f"/api/tweets/{2}/likes?api_key={other_api_key}")
    assert response.status_code == 200
    response = await client.post(f"/api/tweets/{3}/likes?api_key={api_key}")
    assert response.status_code == 200

    # 4) get list of tweets
    response = await client.get(BASE_ROUTE.format(api_key=api_key))
    assert response.status_code == 200
    # check response json
    response_json: Dict[str, Any] = response.json()
    assert response_json["result"] is True
    assert "tweets" in response_json
    assert isinstance(response_json["tweets"], list)
    assert len(response_json["tweets"]) == 3
    # check order of tweets - must be 2, 3, 1
    for expected_id, tweet_json in zip((2, 3, 1), response_json["tweets"]):
        assert tweet_json["id"] == expected_id
        assert "content" in tweet_json
        assert "attachments" in tweet_json
        assert "author" in tweet_json
        assert tweet_json["author"]["id"] == other_user_id
        assert "likes" in tweet_json


@pytest.mark.asyncio
async def test_get_list_of_tweets_with_images(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing getting a tweet feed with images"""
    user_id, api_key = user_data
    other_user_id, other_api_key = other_user_data

    # 1) Subscribe one user to another
    response = await client.post(f"/api/users/{other_user_id}/follow?api_key={api_key}")
    assert response.status_code == 200

    # 2) Add 9 images
    images_ids: List[int] = list()
    for _ in range(9):
        response = await client.post(
            "/api/medias?api_key={}".format(other_api_key),
            files={
                "image": (
                    "test.jpg",
                    open("tests/test_routes/images/test.jpg", "rb"),
                    "multipart/form-data",
                )
            },
        )
        assert response.status_code == 201
        images_ids.append(response.json()["media_id"])

    # 3) Create three tweets with images from other user
    for num in range(3):
        new_tweet: Dict = {
            "tweet_data": "test_tweet_text",
            "tweet_media_ids": images_ids[num * 3 : (num + 1) * 3],
        }
        response = await client.post(
            f"/api/tweets?api_key={other_api_key}", json=new_tweet
        )
        assert response.status_code == 201

    # 4) Like twice 2, once 3 and don't like 1 tweets
    response = await client.post(f"/api/tweets/{2}/likes?api_key={api_key}")
    assert response.status_code == 200
    response = await client.post(f"/api/tweets/{2}/likes?api_key={other_api_key}")
    assert response.status_code == 200
    response = await client.post(f"/api/tweets/{3}/likes?api_key={api_key}")
    assert response.status_code == 200

    # 5) get list of tweets
    response = await client.get(BASE_ROUTE.format(api_key=api_key))
    assert response.status_code == 200
    # check response json
    response_json: Dict[str, Any] = response.json()
    assert response_json["result"] is True
    assert "tweets" in response_json
    assert isinstance(response_json["tweets"], list)
    assert len(response_json["tweets"]) == 3
    # check order of tweets - must be 2, 3, 1
    for expected_id, tweet_json in zip((2, 3, 1), response_json["tweets"]):
        assert tweet_json["id"] == expected_id
        assert "content" in tweet_json
        assert "attachments" in tweet_json
        assert len(tweet_json["attachments"]) == 3
        assert "author" in tweet_json
        assert tweet_json["author"]["id"] == other_user_id
        assert "likes" in tweet_json

    # 6) delete images
    await delete_images_by_ids(images_ids)


@pytest.mark.asyncio
async def test_get_info_about_user_with_invalid_api_key(client: AsyncClient) -> None:
    """Negative test of getting tweet feed with invalid api_key"""
    invalid_api_key = "invalid_api_key"

    # try getting info about user
    response = await client.get(BASE_ROUTE.format(api_key=invalid_api_key))
    assert response.status_code == 401
