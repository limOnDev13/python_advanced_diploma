import pytest

BASE_ROUTE: str = "/api/medias?api_key={}"
TEST_IMAGE_PATH: str = "tests/test_routes/images/test.jpg"
LARGE_IMAGE_PATH: str = "tests/test_routes/images/large_image.png"
FILE_WITH_WRONG_FORMAT: str = "tests/test_routes/images/wrong_format.txt"


@pytest.mark.asyncio
async def test_add_image(client, user_data: tuple[int, str]) -> None:
    """Testing saving several images"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
    )
    assert response.status_code == 201
    image_id: int = response.json()["image_id"]
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
    )
    assert response.status_code == 201
    assert image_id + 1 == response.json()["image_id"]


@pytest.mark.asyncio
async def test_invalid_api_key(client) -> None:
    """Negative testing of saving image with invalid api_key"""
    response = await client.post(
        BASE_ROUTE.format("wrong_api_key"),
        files={
            "image": ("test.jpg", open(TEST_IMAGE_PATH, "rb"), "multipart/form-data")
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_large_image(client, user_data: tuple[int, str]) -> None:
    """Negative testing of saving image with large size (more 2 MB)"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": (
                "large_image.png",
                open(LARGE_IMAGE_PATH, "rb"),
                "multipart/form-data",
            )
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_file_with_wrong_format(client, user_data: tuple[int, str]) -> None:
    """Negative testing of saving file with"""
    _, api_key = user_data
    response = await client.post(
        BASE_ROUTE.format(api_key),
        files={
            "image": (
                "wrong_format.txt",
                open(FILE_WITH_WRONG_FORMAT, "rb"),
                "multipart/form-data",
            )
        },
    )
    assert response.status_code == 403
