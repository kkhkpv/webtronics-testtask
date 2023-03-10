from datetime import datetime, timedelta
from src.config import settings
from jose import jwt, JWTError
import src.schemas as schemas
from fastapi import HTTPException


def create_access_token(data: dict) -> str:
    expires_delta: timedelta = timedelta(minutes=settings.jwt_exp)

    to_encode = data.copy()

    to_encode["exp"] = datetime.utcnow() + expires_delta

    token = jwt.encode(to_encode, key=settings.jwt_key,
                       algorithm=settings.jwt_algo)
    return token


def verify_token(token: str, credential_exception: HTTPException) -> schemas.TokenData:
    try:
        payload = jwt.decode(token, key=settings.jwt_key,
                             algorithms=settings.jwt_algo)
    except JWTError:
        raise credential_exception
    user_id = payload.get("id")
    if user_id is None:
        raise credential_exception
    return {"user_id": user_id}
