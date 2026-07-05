from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard response envelope used by every endpoint: {data, error, message}."""

    data: Optional[T] = None
    error: Optional[str] = None
    message: str = ""
