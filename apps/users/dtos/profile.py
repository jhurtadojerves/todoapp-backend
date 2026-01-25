from typing import Optional

from pydantic import BaseModel


class ProfileData(BaseModel):
    bio: Optional[str] = None
    avatar: Optional[str] = None
