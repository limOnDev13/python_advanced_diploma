
import re

from fastapi import UploadFile
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.queries import add_image


def _file_extension(filename: str) -> str:
    """
    Function returns the file extension
    :param filename: File name
    :return: File extension
    """
    match = re.search(r".*\.(.*?)$", filename)
    extension: str = match.group(1)
    return extension


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
    with Image.open(image_file.file) as image:
        img_extension: str = _file_extension(image_file.filename)
        image_id: int = await add_image(session)
        image.save(f"./static/images/{image_id}.{img_extension}")
        return image_id

