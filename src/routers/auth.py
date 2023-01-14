from fastapi import APIRouter, security, Depends, HTTPException, status
from src.dependencies import get_session
import src.schemas as schemas
import src.models as models
from src.database import AsyncSession
from sqlalchemy import select
import src.jwt as jwt


router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
async def user_login(
    user_creds: security.OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
) -> schemas.TokenResponse:

    select_query = select(models.User).where(
        models.User.email == user_creds.username)
    user = await session.execute(select_query)
    user = user.scalar()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    if not user.verify_password(user_creds.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    access_token: str = jwt.create_access_token(user.id)
    return {
        "token": access_token,
        "token_type": "bearer"
    }
