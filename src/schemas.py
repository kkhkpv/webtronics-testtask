from pydantic import BaseModel, EmailStr, Field, validator
import orjson
import re
from datetime import datetime


PASSWORD_PATTERN = re.compile(
    r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])[0-9a-zA-Z!@#$%^&*]{6,}")


def orjson_dumps(v, *, default) -> str:
    return orjson.dumps(v, default=default).decode()


class ORJSONModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class UserBase(ORJSONModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str = Field(min_length=6)

    @validator("password")
    def valid_password(cls, password: str) -> str | None:
        if not re.match(PASSWORD_PATTERN, password):
            raise ValueError("password is not strong")

        return password


class UserAuth(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True


class TokenResponse(ORJSONModel):
    token: str
    token_type: str


class TokenData(ORJSONModel):
    user_id: int | None


class PostBase(ORJSONModel):
    title: str
    content: str
    published: bool = True

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner: UserResponse

    class Config:
        orm_mode = True


class PostResponse(ORJSONModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True
