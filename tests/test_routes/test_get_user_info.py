from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/users/{user_id}"


@pytest.mark.asyncio
async def test_get_info_about_other_user_without_followers_and_following(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Testing getting info about user without followers and following"""
    user_id, _ = user_data

    # get info about user
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    # check response.json()
    response_json: dict = response.json()
    assert response_json["result"] is True
    assert response_json["id"] == user_id
    assert isinstance(response_json["followers"], list)
    assert isinstance(response_json["following"], list)
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 0
    assert "api_key" not in response_json


@pytest.mark.asyncio
async def test_get_info_about_not_existing_user(client: AsyncClient) -> None:
    """Negative test of getting info about not existing user"""
    not_existing_user_id: int = 100

    # try getting info about user
    response = await client.get(BASE_ROUTE.format(user_id=not_existing_user_id))
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_info_about_other_user_with_followers(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing getting info about user with followers and without following"""
    user_id, _ = user_data
    other_user_id, other_user_api_key = other_user_data

    # get info
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    response_json: dict = response.json()
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 0

    # add follower
    response = await client.post(
        f"/api/users/{user_id}/follow", headers={"api-key": other_user_api_key}
    )
    assert response.status_code == 200

    # get new info
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    # check response.json()
    response_json = response.json()
    assert len(response_json["followers"]) == 1
    assert len(response_json["following"]) == 0
    assert response_json["followers"][0]["id"] == other_user_id


@pytest.mark.asyncio
async def test_get_info_about_other_user_with_following(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing getting info about user with following and without followers"""
    user_id, api_key = user_data
    other_user_id, _ = other_user_data

    # get info
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    response_json: dict = response.json()
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 0

    # add following
    response = await client.post(
        f"/api/users/{other_user_id}/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 200

    # get new info
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    # check response.json()
    response_json = response.json()
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 1
    assert response_json["following"][0]["id"] == other_user_id


@pytest.mark.asyncio
async def test_get_info_about_other_user_with_following_and_followers(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing getting info about user with following and followers"""
    user_id, api_key = user_data
    other_user_id, other_user_api_key = other_user_data

    # get info about user
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    response_json: dict = response.json()
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 0
    # get info about other user
    response = await client.get(BASE_ROUTE.format(user_id=other_user_id))
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["followers"]) == 0
    assert len(response_json["following"]) == 0

    # Subscribe both users to each other
    response = await client.post(
        f"/api/users/{other_user_id}/follow", headers={"api-key": api_key}
    )
    assert response.status_code == 200
    response = await client.post(
        f"/api/users/{user_id}/follow", headers={"api-key": other_user_api_key}
    )
    assert response.status_code == 200

    # get new info
    response = await client.get(BASE_ROUTE.format(user_id=user_id))
    assert response.status_code == 200
    # check response.json()
    response_json = response.json()
    assert len(response_json["followers"]) == 1
    assert len(response_json["following"]) == 1
    assert response_json["following"][0]["id"] == other_user_id
    assert response_json["followers"][0]["id"] == other_user_id

    response = await client.get(BASE_ROUTE.format(user_id=other_user_id))
    assert response.status_code == 200
    # check response.json()
    response_json = response.json()
    assert len(response_json["followers"]) == 1
    assert len(response_json["following"]) == 1
    assert response_json["following"][0]["id"] == user_id
    assert response_json["followers"][0]["id"] == user_id
