from pydantic import BaseModel


class UserData(BaseModel):
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    password: str
