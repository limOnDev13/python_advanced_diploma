from typing import List, Optional

from pydantic import BaseModel, Field


class TweetSchema(BaseModel):
    tweet_data: str = Field(
        default=...,
        title="The text of the tweet",
        description="The text of the tweet",
    )
    tweet_media_ids: Optional[List[int]] = Field(
        default=None,
        title="List of image IDs",
        description="List of image IDs. An optional parameter. "
        "The frontend will upload images there "
        "automatically when sending a tweet and"
        " substitute the id from there in json.",
    )


class UserSchema(BaseModel):
    id: int = Field(default=..., description="User id")
    name: str = Field(default=..., description="User's name")


class UserOutSchema(BaseModel):
    result: bool = True
    id: int = Field(default=..., description="User id")
    name: str = Field(default=..., description="User's name")
    followers: List[UserSchema] = Field(
        default_factory=list, description="List of followers"
    )
    following: List[UserSchema] = Field(
        default_factory=list, description="List of authors subscribed to by users"
    )

    class ConfigDict:
        orm_mod = True


class ErrorSchema(BaseModel):
    result: bool = False
    error_type: str = Field(default=..., description="Type of exception")
    error_message: str = Field(default=..., description="Error message")
