"""The module is responsible for database queries"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Session
from models import User


async def user_table_has_rows(session: AsyncSession) -> bool:
    """
    The function checks if there are records in the User table
    :param session: session's object
    :type session: AsyncSession
    :return: True, if table User has rows, else False
    :rtype: bool
    """
    exists = await session.execute(select(User))
    return exists.first() is not None


async def create_user(session: AsyncSession, user_dict: dict[str, str]) -> None:
    """
    The function adds the user to the database
    :param session: session's object
    :type session: AsyncSession
    :param user_dict: The user's data
    :type user_dict: dict[str, str]
    :return: None
    """
    async with session.begin():
        session.add(User(**user_dict))
