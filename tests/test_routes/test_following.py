from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/users/{user_id}/follow"


@pytest.mark.asyncio
async def test_follow_author(
    client: AsyncClient, user_data: Tuple[int, str], other_user_data: Tuple[int, str]
) -> None:
    """Testing following author"""
    user_id, api_key = user_data
    other_user_id, _ = other_user_data

    # follow author
    response = await client.post(
        BASE_ROUTE.format(user_id=other_user_id), headers={"api-key": api_key}
    )
    assert response.status_code == 200
    # try again follow author
    response = await client.post(
        BASE_ROUTE.format(user_id=other_user_id), headers={"api-key": api_key}
    )
    assert response.status_code == 400
    # try follow yourself
    response = await client.post(
        BASE_ROUTE.format(user_id=user_id), headers={"api-key": api_key}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_follow_with_invalid_api_key(
    client: AsyncClient, other_user_data
) -> None:
    """Negative test of following with invalid api_key"""
    other_user_id, _ = other_user_data
    invalid_api_key: str = "invalid_api_key"

    response = await client.post(
        BASE_ROUTE.format(user_id=other_user_id), headers={"api-key": invalid_api_key}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_follow_not_existing_user(
    client: AsyncClient, user_data: Tuple[int, str]
) -> None:
    """Negative test of following not existing user"""
    _, api_key = user_data
    invalid_user_id: int = 100

    response = await client.post(
        BASE_ROUTE.format(user_id=invalid_user_id), headers={"api-key": api_key}
    )
    assert response.status_code == 404
