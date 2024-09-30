import re
from logging import getLogger
from typing import Optional

import aiofiles.os

logger = getLogger("image_logger.func")


async def get_image_name_by_id(image_id, images_path) -> Optional[str]:
    """Function returns image name by id"""
    logger.info(
        "Start searching image name with id %d in dir %s", image_id, images_path
    )
    for filename in await aiofiles.os.listdir(images_path):
        logger.debug("Current filename - %s", filename)
        if re.fullmatch(rf"{image_id}\..*?$", filename):
            logger.info("The file %s fits - returns", filename)
            return filename
        logger.debug("The file %s does not fit", filename)
    logger.warning("No matches")
    return None
