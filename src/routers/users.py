from fastapi import APIRouter, Depends, HTTPException, status
import models
import schemas
import dependencies
from database import AsyncSession
from sqlalchemy import select
import passlib.hash as hash


router = APIRouter()


@router.post("/users", response_model=schemas.UserResponse)
async def create_user(
    user: schemas.UserCreate,
    session: AsyncSession = Depends(dependencies.get_session)
) -> schemas.UserResponse:
    select_query = select(models.User).where(models.User.email == user.email)
    candidate = await session.execute(select_query)
    if candidate.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email taken")
    user_to_add = models.User(
        email=user.email, hashed_password=hash.bcrypt.hash(user.password))
    session.add(user_to_add)
    await session.commit()
    await session.refresh(user_to_add)

    return {
        "id": user_to_add.id,
        "email": user.email
    }


@router.get("/users/{id_}", response_model=schemas.UserResponse)
async def get_user(
    id_: int,
    session: AsyncSession = Depends(dependencies.get_session)
) -> schemas.UserResponse:
    select_query = select(models.User).where(models.User.id == id_)
    user = await session.execute(select_query)
    user = user.scalar()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id_} wasn't found")

    return {
        "id": user.id,
        "email": user.email
    }
