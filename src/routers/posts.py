from fastapi import APIRouter, HTTPException, status, Depends, Response
import src.schemas as schemas
from src.database import AsyncSession
from src.dependencies import get_session, verify_current_user
from sqlalchemy import select, func, desc, update, delete
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
    posts = await session.execute(select_query)
    posts = posts.all()
    return posts


@router.get("/{id_}", response_model=schemas.PostResponse)
async def get_post_by_id(
    id_: int,
    session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user)
) -> schemas.PostResponse:
    select_query = select(models.Post, func.count(models.Likes.post_id).label("likes"))\
        .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
        .group_by(models.Post.id)\
        .filter(models.Post.id == id_)
    post = await session.execute(select_query)
    try:
        post = post.one()
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id_} wasn't found"
        )
    if not (post.Post.published) and post.Post.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id_} wasn/t found"
        )
    return post


@router.post("/", response_model=schemas.Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: schemas.PostCreate,
    session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user)
) -> schemas.Post:
    post_to_add = models.Post(**dict(post), owner_id=owner.id)
    session.add(post_to_add)
    await session.commit()
    await session.refresh(post_to_add)
    return post_to_add


@router.put("/visibility_change/{id_}", status_code=status.HTTP_200_OK)
async def change_visibility(
    id_: int, session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user)
) -> str:
    select_query = select(models.Post).where(models.Post.id == id_)
    post = await session.execute(select_query)
    candidate = post.scalar()

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="post wasn't found"
        )

    if candidate.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unauthorized action"
        )
    update_data = {
        "published": not candidate.published
    }
    query = update(models.Post).where(models.Post.id == id_)\
        .values(**update_data).execution_options(synchronize_session="fetch")
    await session.execute(query)
    await session.commit()
    return f"Visibility of post {id_} has been changed"


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id_: int, session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user)
):
    select_query = select(models.Post).where(models.Post.id == id_)
    candidate = await session.execute(select_query)
    candidate = candidate.scalar()

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id_} wasn't found"
        )
    if candidate.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unauthorized action"
        )
    delete_query = delete(models.Post).where(models.Post.id == id_)
    await session.execute(delete_query)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id_}", status_code=status.HTTP_200_OK)
async def update_post(
    id_: int, post: schemas.PostCreate,
    session: AsyncSession = Depends(get_session),
    owner: models.User = Depends(verify_current_user)
):
    select_query = select(models.Post).where(models.Post.id == id_)
    candidate = await session.execute(select_query)
    candidate = candidate.scalar()

    if candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id_} wasn't found"
        )
    if candidate.owner_id != owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="unauthorized action"
        )
    query = update(models.Post).where(models.Post.id == id_)\
        .values(**dict(post)).execution_options(synchronize_session="fetch")
    await session.execute(query)
    await session.commit()
    return Response(status_code=status.HTTP_200_OK)
