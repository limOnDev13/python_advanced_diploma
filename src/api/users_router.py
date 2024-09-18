import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import models
from src.database import queries as q
from src.schemas import schemas
from src.service.web import check_api_key, check_users_exists, get_session

users_router = APIRouter(tags=["users"])

logger = logging.getLogger("routes_logger.users_logger")


@users_router.post(
    "/api/users/{user_id}/follow",
    status_code=200,
    responses={
        400: {
            "description": "The user has already subscribed to the author",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "The user {follower.id}"
                        " is already following the author {author.id}",
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
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
        403: {
            "description": "A follower cannot subscribe to himself",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "A follower cannot subscribe to himself",
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "NotFoundError",
                        "error_message": "User {user_id} not found",
                    }
                }
            },
        },
        200: {
            "description": "The user has tagged the author",
            "content": {"application/json": {"example": {"result": True}}},
        },
    },
)
async def follow_user(
    follower: models.User = Depends(check_api_key),
    author: models.User = Depends(check_users_exists),
    session: AsyncSession = Depends(get_session),
):
    """
    Endpoint for a follower's subscription to the author
    """
    logger.info("Start following the user")
    logger.debug("follower.id=%d, author.id=%d", follower.id, author.id)

    # follower can't follow himself
    if follower.id == author.id:
        logger.warning("You can't subscribe to yourself")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A follower cannot subscribe to himself",
        )
    try:
        await q.follow_author(session, follower, author)
    except ValueError as exc:
        logger.warning(str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    logger.info("Successful following")

    return {"result": True}


@users_router.delete(
    "/api/users/{user_id}/follow",
    status_code=200,
    responses={
        400: {
            "description": "The user has already unsubscribed from the author",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "The follower {follower.id} has already"
                        " been unsubscribed from the author {author.id}",
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
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
        403: {
            "description": "A follower cannot unfollow to himself",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "HTTPException",
                        "error_message": "A follower cannot unsubscribe to himself",
                    }
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "NotFoundError",
                        "error_message": "User {user_id} not found",
                    }
                }
            },
        },
        200: {
            "description": "The user has unfollowed the author",
            "content": {"application/json": {"example": {"result": True}}},
        },
    },
)
async def unfollow_user(
    follower: models.User = Depends(check_api_key),
    author: models.User = Depends(check_users_exists),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint for unsubscribing from the author
    """
    logger.info("Start unfollowing the author")
    logger.debug("follower.id=%d, author.id=%d", follower.id, author.id)

    # follower can't unfollow to himself
    if follower.id == author.id:
        logger.warning("Follower can't unfollow to himself")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A follower cannot unsubscribe to himself",
        )
    try:
        await q.unfollow_author(session, follower, author)
    except ValueError as exc:
        logger.warning(str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    logger.info("Successful unfollowing")

    return {"result": True}


@users_router.get(
    "/api/users/me",
    status_code=200,
    response_model=schemas.UserOutSchema,
    responses={
        401: {
            "description": "api_key not exists",
            "content": {
                "application/json": {
                    "example": {
                        "result": False,
                        "error_type": "IdentificationError",
                        "error_message": "api_key {api_key} not exists",
                    }
                }
            },
        },
    },
)
async def get_current_user_info(
    user: models.User = Depends(check_api_key),
    session: AsyncSession = Depends(get_session),
):
    """
    The endpoint for getting info about a current user
    """
    logger.info("Start getting user info")
    logger.debug("User followers: %s", str(user.followers))
    logger.debug("The user is subscribed to the authors: %s", str(user.authors))
    return user.full_json()
