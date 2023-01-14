from fastapi import APIRouter, Depends, HTTPException, status
from src.dependencies import get_session, verify_current_user, AsyncSession
import src.schemas as schemas
import src.models as models
from sqlalchemy import select, delete

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def rate_post(
    rate: schemas.Rate,
    session: AsyncSession = Depends(get_session),
    user: models.User = Depends(verify_current_user)
) -> dict:
    post_select_query = select(models.Post).where(
        models.Post.id == rate.post_id, models.Post.published == True)
    post = await session.execute(post_select_query)
    post = post.scalar()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="post wasn't found"
        )
    if post.owner_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user tried to rate his own post"
        )
    likes_select_query = select(models.Likes)\
        .where(models.Likes.post_id == rate.post_id, models.Likes.user_id == user.id)
    rating = await session.execute(likes_select_query)
    rating = rating.scalars()

    if rate.dir == 1:
        if rating is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="rating already exist")
        rating_to_add = models.Likes(user_id=user.id, post_id=rate.post_id)
        session.add(rating_to_add)
    elif rate.dir == 0:
        if rating is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="rating doesnt exist")
        delete_query = delete(models.Likes).where(
            models.Likes.post_id == rate.post_id, models.Likes.user_id == user.id)
        await session.execute(delete_query)
    await session.commit()
    return dict()
