from pydantic import BaseModel
from typing import Optional


class PushRequest(BaseModel):
    do_reset: Optional[int] = 0


class SearcRequest(BaseModel):
    text: str
    limit: Optional[int] = 5
