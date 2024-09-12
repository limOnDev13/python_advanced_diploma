from typing import List, Optional

from pydantic import BaseModel, Field


class Tweet(BaseModel):
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
