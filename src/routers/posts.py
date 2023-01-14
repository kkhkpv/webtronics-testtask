from fastapi import APIRouter, HTTPException, status, Depends
import src.schemas as schemas
from src.database import AsyncSession
from src.dependencies import get_session, verify_current_user
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
import src.models as models
from src.jwt import verify_token

router = APIRouter()


@router.get("/", response_model=list[schemas.PostResponse])
async def get_posts(
    session: AsyncSession = Depends(get_session),
    limit: int = 10, skip: int = 0, search: str = ""
) -> list[schemas.PostResponse]:
    select_query = select(models.Post, func.count(models.Likes.post_id).label("likes"))\
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.title.contains(search), models.Post.published == True)\
        .options(selectinload(models.Post.owner))\
        .order_by(desc(models.Post.created_at))\
        .limit(limit).offset(skip)
    posts = await session.execute(select_query)
    posts = posts.all()
    # print(posts)
    return posts


@router.get("/latest", response_model=schemas.PostResponse)
async def get_latest_post(session: AsyncSession = Depends(get_session)) -> schemas.PostResponse:
    select_query = select(models.Post, func.count(models.Likes.post_id).label("likes"))\
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.published == True)\
        .options(selectinload(models.Post.owner))\
        .order_by(desc(models.Post.created_at))\
        .limit(1)
    post = await session.execute(select_query)
    post = post.one()

    return post


@router.get("/my", response_model=list[schemas.PostResponse])
async def get_my_posts(
    session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user),
    limit: int = 10, skip: int = 0, search: str = ""
) -> list[schemas.PostResponse]:
    select_query = select(models.Post, func.count(models.Likes.post_id).label("likes"))\
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.title.contains(search), models.Post.owner_id == owner.id)\
        .order_by(desc(models.Post.created_at))\
        .limit(limit).offset(skip)
    posts = await session.execute()
    posts = posts.all()
    return posts
