from typing import Tuple

import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/users/{user_id}/follow"


@pytest.mark.asyncio
async def test_unfollow_author(
    client: AsyncClient,
    follower_api_key_and_author_id: Tuple[str, int],
    user_data: Tuple[int, str],
) -> None:
    """Testing unfollowing from author"""
    follower_api_key, author_id = follower_api_key_and_author_id
    follower_id, _ = user_data

    # unfollow author
    response = await client.delete(
        BASE_ROUTE.format(user_id=author_id), headers={"api-key": follower_api_key}
    )
    assert response.status_code == 200

    # try again unfollowing author
    response = await client.delete(
        BASE_ROUTE.format(user_id=author_id), headers={"api-key": follower_api_key}
    )
    assert response.status_code == 400

    # try unfollowing yourself
    response = await client.delete(
        BASE_ROUTE.format(user_id=follower_id), headers={"api-key": follower_api_key}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unfollow_with_invalid_api_key(
    client: AsyncClient, follower_api_key_and_author_id
) -> None:
    """Negative test of unfollowing with invalid api_key"""
    _, author_id = follower_api_key_and_author_id
    invalid_api_key: str = "invalid_api_key"

    response = await client.delete(
        BASE_ROUTE.format(user_id=author_id), headers={"api-key": invalid_api_key}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unfollow_not_existing_user(
    client: AsyncClient, follower_api_key_and_author_id: Tuple[str, int]
) -> None:
    """Negative test of unfollowing from not existing author"""
    follower_api_key, _ = follower_api_key_and_author_id
    invalid_author_id: int = 100

    response = await client.delete(
        BASE_ROUTE.format(user_id=invalid_author_id),
        headers={"api-key": follower_api_key},
    )
    assert response.status_code == 404
