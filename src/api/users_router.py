import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import models
from src.database import queries as q
from src.schemas import schemas
from src.service.web import check_api_key, check_users_exist

users_router = APIRouter(tags=["users"])

logger = logging.getLogger("routes_logger.users_logger")


@users_router.post(
    "/api/users/{user_id}/follow",
    status_code=200,
    dependencies=[Depends(check_api_key)],
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
async def follow_user(request: Request, user_id: int):
    """
    Endpoint for a follower's subscription to the author
    """
    logger.info("Start following the user")
    session: AsyncSession = request.state.session
    follower: models.User = request.state.current_user
    author: models.User = await check_users_exist(user_id, session)

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
    dependencies=[Depends(check_api_key)],
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
    request: Request,
    user_id: int,
):
    """
    The endpoint for unsubscribing from the author
    """
    logger.info("Start unfollowing the author")
    # check api-key from headers
    session: AsyncSession = request.state.session
    follower: models.User = request.state.current_user
    author: models.User = await check_users_exist(user_id, session)

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


def _get_user_info(user: models.User) -> Dict[str, Any]:
    logger.info("Start getting user info")
    logger.debug("User followers: %s", str(user.followers))
    logger.debug("The user is subscribed to the authors: %s", str(user.authors))
    return user.full_json()


@users_router.get(
    "/api/users/me",
    status_code=200,
    response_model=schemas.UserOutSchema,
    dependencies=[Depends(check_api_key)],
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
    request: Request,
):
    """
    The endpoint for getting info about a current user
    """
    logger.info("Getting info about current user")
    # check api-key from headers
    user: models.User = request.state.current_user

    return _get_user_info(user)


@users_router.get(
    "/api/users/{user_id}",
    status_code=200,
    response_model=schemas.UserOutSchema,
    responses={
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
    },
)
async def get_user_info(user_id: int, request: Request):
    """
    The endpoint for getting info about user
    """
    session = request.state.session
    user: models.User = await check_users_exist(user_id, session)
    return _get_user_info(user)
