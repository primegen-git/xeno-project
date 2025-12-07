from contextlib import asynccontextmanager
from typing import AsyncGenerator

import models
from database import engine, get_db
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.events import router as events_router
from routers.fetch_database import router as fetch_database_router
from routers.shopify_sync import router as shopify_sync_router
from routers.shops import router as shops_router
from routers.webhooks import router as webhooks_router
from sqlalchemy import select
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # models.Base.metadata.create_all(bind=engine)  # should not be run in production.
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "https://xeno-project-wm1j.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def hello_world():
    return {"hello, world"}


@app.get("/database-check")
async def check_database(db: Session = Depends(get_db)):
    stmt = select(models.Dummy).where(models.Dummy.id == 1)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        return {"message": "no message exist"}
    return {"id": result.id, "message": result.message}


app.include_router(router=shops_router, prefix="/shops", tags=["shops"])
app.include_router(router=shopify_sync_router, prefix="/sync", tags=["shops"])
app.include_router(router=fetch_database_router, prefix="/fetch", tags=["shops"])
app.include_router(router=auth_router, prefix="/auth", tags=["shops"])
app.include_router(router=webhooks_router, prefix="/webhooks", tags=["shops"])
app.include_router(router=events_router, tags=["events"])
