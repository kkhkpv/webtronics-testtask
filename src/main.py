from fastapi import FastAPI
from models import *
from database import init_models
from routers.users import router as user_router
from routers.auth import router as auth_router
from routers.posts import router as posts_router

app = FastAPI()


@app.on_event("startup")
async def startup() -> None:
    await init_models()


@app.get("/test", include_in_schema=False)
async def test() -> dict[str, str]:
    return {
        "status": "ok"
    }


app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(posts_router, prefix="/posts")
