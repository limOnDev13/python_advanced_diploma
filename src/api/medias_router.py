from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.service.images import upload_image, validate_image
from src.service.web import check_api_key

medias_router: APIRouter = APIRouter(
    tags=["medias"], dependencies=[Depends(check_api_key)]
)

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
async def save_image(file: UploadFile, request: Request):
    """
    The endpoint saves the image to disk
    """
    logger.info("Start saving image")
    # check api-key from headers
    session: AsyncSession = request.state.session

    try:
        logger.debug("Validating image")
        validate_image(file)

        logger.debug("Trying to upload an image")
        image_id: int = await upload_image(file, session)
        logger.debug("Image was uploaded, image_id=%s", image_id)

        return {"result": True, "media_id": image_id}
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
        await file.close()
