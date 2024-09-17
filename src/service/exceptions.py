from typing import Any, Optional, Dict

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from src.schemas.schemas import ErrorSchema


async def http_exception_handler(request: Request, exc: HTTPException):
    content = ErrorSchema(error_type=type(exc).__name__, error_message=exc.detail).model_dump(mode="json")
    return JSONResponse(content, status_code=exc.status_code)


class IdentificationError(HTTPException):
    def __init__(
            self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class NotFoundError(HTTPException):
    def __init__(
            self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class ForbiddenError(HTTPException):
    def __init__(
            self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)
