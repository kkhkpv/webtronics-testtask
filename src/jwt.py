from datetime import datetime, timedelta
from src.config import settings
from jose import jwt


def create_access_token(id: int) -> str:
    expires_delta: timedelta = timedelta(minutes=settings.jwt_exp)
    to_encode = {
        "id": id,
        "exp": datetime.utcnow() + expires_delta
    }

    token = jwt.encode(to_encode, key=settings.jwt_key,
                       algorithm=settings.jwt_algo)
    return token
