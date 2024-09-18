from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.images import upload_image, validate_image
from src.service.web import check_api_key, get_session

medias_router: APIRouter = APIRouter()

logger = getLogger("routes_logger.medias_logger")


@medias_router.post(
    "/api/medias",
    status_code=201,
    responses={
        400: {
            "description": "Something went wrong when uploading the image",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "error type",
                        "error_message": "error message",
                    }
                }
            },
        },
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key <api_key> not exists",
                    }
                }
            },
        },
        403: {
            "description": "Image size too large or image has invalid format",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "error type",
                        "error_message": "error message",
                    }
                }
            },
        },
        201: {
            "description": "Image was saved",
            "content": {
                "application/json": {"example": {"result": True, "media_id": 1}}
            },
        },
    },
)
async def save_image(
    image: UploadFile,
    user_id: int = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint saves the image to disk
    """
    logger.info("Start saving image")

    try:
        logger.debug("Validating image")
        validate_image(image)

        logger.debug("Trying to upload an image")
        image_id: int = await upload_image(image, session)
        logger.debug("Image was uploaded, image_id=%s", image_id)

        return {"result": True, "image_id": image_id}
    except ValueError as exc:
        logger.warning("Image too large", exc_info=exc)
        raise HTTPException(detail=str(exc), status_code=403)
    except TypeError as exc:
        logger.warning("Wrong image format", exc_info=exc)
        raise HTTPException(detail=str(exc), status_code=403)
    except Exception as exc:
        logger.exception("Smth wrong", exc_info=exc)
        raise HTTPException(detail=str(exc), status_code=400)
    finally:
        await image.close()
