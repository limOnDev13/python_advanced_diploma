import pytest
from httpx import AsyncClient

BASE_ROUTE: str = "/api/medias"
TEST_IMAGE_PATH: str = "tests/test_routes/images/test.jpg"
LARGE_IMAGE_PATH: str = "tests/test_routes/images/large_image.png"
FILE_WITH_WRONG_FORMAT: str = "tests/test_routes/images/wrong_format.txt"


@pytest.mark.asyncio
async def test_add_image(client: AsyncClient, user_data: tuple[int, str]) -> None:
    """Testing saving several images"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE,
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
        headers={"api-key": api_key},
    )
    assert response.status_code == 201
    assert response.json()["result"] is True
    image_id: int = response.json()["media_id"]
    response = await client.post(
        BASE_ROUTE,
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
        headers={"api-key": api_key},
    )
    assert response.status_code == 201
    assert image_id + 1 == response.json()["media_id"]


@pytest.mark.asyncio
async def test_send_img_with_invalid_api_key(client: AsyncClient) -> None:
    """Negative testing of saving image with invalid api_key"""
    response = await client.post(
        BASE_ROUTE,
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
        headers={"api-key": "invalid_api_key"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_large_image(client: AsyncClient, user_data: tuple[int, str]) -> None:
    """Negative testing of saving image with large size (more 2 MB)"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE,
        files={
            "image": (
                "large_image.png",
                open(LARGE_IMAGE_PATH, "rb"),
                "multipart/form-data",
            )
        },
        headers={"api-key": api_key},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_file_with_wrong_format(
    client: AsyncClient, user_data: tuple[int, str]
) -> None:
    """Negative testing of saving file with"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE,
        files={
            "image": (
                "wrong_format.txt",
                open(FILE_WITH_WRONG_FORMAT, "rb"),
                "multipart/form-data",
            )
        },
        headers={"api-key": api_key},
    )
    assert response.status_code == 403
