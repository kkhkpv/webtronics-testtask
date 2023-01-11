from fastapi import FastAPI
from models import *
from database import init_models
from routers.users import router as user_router


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
