from fastapi import FastAPI
from src.models import User, Likes, Post
from src.database import init_models
from src.routers.users import router as user_router
from src.routers.auth import router as auth_router
from src.routers.posts import router as posts_router
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origins=origins
)


@app.on_event("startup")
async def startup() -> None:
    await init_models()


@app.get("/test", include_in_schema=False)
async def test() -> dict[str, str]:
    return {
        "status": "ok",
    }


app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/posts")
