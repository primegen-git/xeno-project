from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from typing import AsyncGenerator
from database import engine, get_db
from routers.shops import router as shops_router
from routers.shopify_sync import router as shopify_sync_router
from routers.fetch_database import router as fetch_database_router
from routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:8080", "http://localhost:3000", "https://xeno-project-wm1j.vercel.app"]

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
