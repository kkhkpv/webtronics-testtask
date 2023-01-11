from datetime import datetime, timedelta
from config import settings
from jose import jwt


def create_access_token(id: int) -> str:
    expires_delta: timedelta = timedelta(minutes=settings.TOKEN_EXP)
    to_encode = {
        "id": id,
        "exp": datetime.utcnow() + expires_delta
    }

    token = jwt.encode(to_encode, key=settings.TOKEN_SECRET, algorithm="HS256")
    return token
