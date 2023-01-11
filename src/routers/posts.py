from fastapi import APIRouter, HTTPException, status, Depends
import schemas
from database import AsyncSession
from dependencies import get_session
from sqlalchemy import select, func, desc
import models

router = APIRouter()


@router.get("/posts", response_model=list[schemas.PostResponse])
async def get_posts(
    session: AsyncSession = Depends(get_session),
    limit: int = 10, skip: int = 0, search: str = ""
) -> list[schemas.PostResponse]:

    select_query = select(models.Post, func.count(models.Likes.post_id).label("likes"))\
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)
    posts = await session.execute(select_query)
    posts = posts.all()
    print(posts)
    return posts
