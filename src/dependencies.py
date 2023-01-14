from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session
from fastapi import security, HTTPException, status, Depends
from src.models import User
from src.jwt import verify_token
from sqlalchemy import select


oauth_schema = security.OAuth2PasswordBearer(tokenUrl="/api/login")


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def verify_current_user(
    token: str = Depends(oauth_schema),
    session: AsyncSession = Depends(get_session)
) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    token_data = verify_token(token, credential_exception)
    select_query = select(User).filter(User.id == token_data.user_id)
    user = await session.execute(select_query)
    user = session.scalar()
    return user
