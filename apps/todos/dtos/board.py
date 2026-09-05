from datetime import date
from typing import Optional

from pydantic import BaseModel


class BoardData(BaseModel):
    name: str
    description: str = ""


class BoardStatusData(BaseModel):
    name: str
    order: int
    color: str = "#000000"


class SprintData(BaseModel):
    name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
