from pydantic import BaseModel


class CommentData(BaseModel):
    content: str
