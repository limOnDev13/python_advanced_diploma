import asyncio
from typing import List, Optional

import pytest

from src.service.func import get_image_name_by_id
from src.service.images import _file_extension, delete_images_by_ids


@pytest.mark.parametrize(
    "filename, result",
    (
        ("file.jpg", "jpg"),
        ("file.txt", "txt"),
        ("/file/file.txt", "txt"),
        ("~/file/file_file/file.txt", "txt"),
        ("file.file.file.txt", "txt"),
    ),
)
def test_file_extension(filename, result) -> None:
    """Testing func _file_extension on several filenames"""
    assert _file_extension(filename) == result


def test_file_extension_with_file_without_extension() -> None:
    """Testing func _file_extension with file without extension"""
    assert _file_extension("test") is None


@pytest.mark.asyncio
async def test_get_image_name_by_id_with_one_image(
    image_id: int, images_path: str
) -> None:
    """Testing function _get_image_by_id with existing one image"""
    assert f"{image_id}.jpg" == await get_image_name_by_id(image_id, images_path)


@pytest.mark.asyncio
async def test_get_image_name_by_id_with_several_images(
    images_ids: List[int], images_path: str
) -> None:
    """Testing function _get_image_by_id with existing several images"""
    images_names: List[Optional[str]] = await asyncio.gather(
        *[get_image_name_by_id(image_id, images_path) for image_id in images_ids]
    )
    assert set(images_names) == set((f"{image_id}.jpg" for image_id in images_ids))


@pytest.mark.asyncio
async def test_get_image_name_by_id_with_not_existing_images(
    images_ids: List[int], images_path: str
) -> None:
    """Testing function _get_image_by_id with not existing images"""
    all_images_ids: List[int] = list()
    all_images_ids.extend(images_ids)
    all_images_ids.extend([num + max(images_ids) for num in range(1, 4)])

    images_names: List[Optional[str]] = await asyncio.gather(
        *[get_image_name_by_id(img_id, images_path) for img_id in images_ids]
    )
    # check existing image_id
    for image_name, img_id in zip(images_names, images_ids):
        assert image_name == f"{img_id}.jpg"
    # check not existing image_id
    for image_name in images_names[len(images_ids) :]:
        assert image_name is None


@pytest.mark.asyncio
async def test_delete_images_by_ids(images_ids: List[int], images_path: str):
    """Testing function delete_images_by_ids with existing images"""
    # check that image not removed
    images_names: List[Optional[str]] = await asyncio.gather(
        *[get_image_name_by_id(img_id, images_path) for img_id in images_ids]
    )
    assert set(images_names) == set((f"{img_id}.jpg" for img_id in images_ids))

    # delete images
    await delete_images_by_ids(images_ids)

    # check that images were removed
    images_names = await asyncio.gather(
        *[get_image_name_by_id(img_id, images_path) for img_id in images_ids]
    )
    for img_name in images_names:
        assert img_name is None


@pytest.mark.asyncio
async def test_delete_images_by_ids_with_not_existing_images(
    images_ids: List[int], images_path
):
    """Testing function delete_images_by_ids with not existing images"""
    not_existing_images_ids: List[int] = [num + max(images_ids) for num in range(1, 4)]

    # check that images not existing
    images_names: List[Optional[str]] = await asyncio.gather(
        *[
            get_image_name_by_id(img_id, images_path)
            for img_id in not_existing_images_ids
        ]
    )
    for image_name in images_names:
        assert image_name is None

    # try deleting these not existing images
    try:
        await delete_images_by_ids(not_existing_images_ids)
    except Exception as exc:
        print(exc)
        pytest.fail()
