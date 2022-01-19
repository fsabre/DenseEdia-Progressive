"""Define the models used by FastAPI."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EdiumSimpleGetModel(BaseModel):
    id: int
    title: str
    kind: Optional[str]
    creation_date: datetime
