import os
import re
from typing import List, Optional, Awaitable
import asyncio

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
import aiofiles.os

from src.database.queries import add_image, get_images_by_ids


def _file_extension(filename: Optional[str]) -> Optional[str]:
    """
    Function returns the file extension
    :param filename: File name
    :return: File extension
    """
    if not filename:
        return None
    match = re.search(r".*\.(.+?)$", filename)
    if not match:
        return None
    return match.group(1)


async def upload_image(image_file: UploadFile, session: AsyncSession) -> int:
    """
    Function saves the image to the database and to disk.
    The name of the saved image will be its id in the database
    :param image_file: The image uploaded via the form
    :type image_file: UploadFile
    :param session: Session object
    :return: Image id
    :rtype: int
    """
    img_extension: Optional[str] = _file_extension(image_file.filename)
    image_id: int = await add_image(session)
    cur_dir_path: str = os.path.dirname(__file__)
    images_path: str = os.path.join(cur_dir_path, "..", "static", "images")

    if not img_extension:
        out_file_path = f"{images_path}/{image_id}"
    else:
        out_file_path = f"{images_path}/{image_id}.{img_extension}"

    async with aiofiles.open(out_file_path, "wb") as out_file:
        content = await image_file.read()
        await out_file.write(content)
    return image_id


def validate_image(image_file: UploadFile) -> None:
    """
    Function validates uploaded image.
    Image must have extension .jpg, .png, .jpeg, .gif;
    image size must be less than 2 MB
    :param image_file: The image uploaded via the form
    :type image_file: UploadFile
    :raise ValueError: If image size more than 2 mb
    :raise TypeError: If image format not in ("jpeg", "jpg", "png", "gif")
    :return: None
    """
    if image_file.size is not None and image_file.size > 2 * 1024 * 1024:
        # more 2 mb
        raise ValueError(
            "Image size must be less than 2 mb; image size is {} MB".format(
                round(image_file.size / 1024 / 1024, 2)
            )
        )
    extension = _file_extension(image_file.filename)
    if extension not in ("jpeg", "jpg", "png", "gif"):
        raise TypeError(
            f"Image must have extensions .jpg, .png, .jpeg, .gif;"
            f" image extension is {extension}"
        )


async def validate_images_in_db(session: AsyncSession, images_ids: List[int]) -> None:
    """
    Function checks that all image ids are in the database
    and these images do not relate to any tweets
    :param session: session object
    :param images_ids: List of images ids
    :type images_ids: List[int]
    :raise ValueError: If some ids are not in the database
    :return: None
    """
    images = await get_images_by_ids(session, images_ids)
    # check - all image ids must be in db
    if len(images) != len(images_ids):
        raise ValueError("Some image_ids not exists")
    # check - these images do not relate to any tweets
    for image in images:
        if image.tweet_id is not None:
            raise ValueError(
                f"Image with id {image.id} relate to tweet with id {image.tweet_id}"
            )


async def delete_images_by_ids(images_ids: List[int]) -> None:
    """Function deletes images from disk by ids"""
    cur_dir_path: str = os.path.dirname(__file__)
    images_path: str = os.path.join(cur_dir_path, "..", "static", "images")
    images_paths: List[str] = [f"{images_path}/{image_id}.*" for image_id in images_ids]
    delete_images_c: List[Awaitable] = [aiofiles.os.remove(path) for path in images_paths]
    await asyncio.gather(*delete_images_c)
