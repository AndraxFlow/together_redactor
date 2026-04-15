from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str


class DocumentUpdate(BaseModel):
    title: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    content: Optional[bytes] = None
