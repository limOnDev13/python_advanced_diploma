from pydantic import BaseModel, Field
from typing import Optional, List


class Tweet(BaseModel):
    tweet_data: str = Field(
        default=...,
        title='The text of the tweet',
        description='The text of the tweet',
    )
    tweet_media_ids: Optional[List[int]] = Field(
        default=None,
        title='List of image IDs',
        description='List of image IDs. An optional parameter. '
                    'The frontend will upload images there '
                    'automatically when sending a tweet and'
                    ' substitute the id from there in json.'
    )


class ErrorDict:
    """
    The class is responsible for bringing exceptions
    to the same format. When __call__ is called, it returns this dictionary.
    Args:
        exc (Exception): exception
    """
    def __init__(self, exc: Exception) -> None:
        self.error_type: str = type(exc).__name__
        self.error_msg: str = str(exc)

    def __call__(self) -> dict[str, str]:
        return {
            "result": False,
            "error_type": self.error_type,
            "error_message": self.error_msg
        }
