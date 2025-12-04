from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from typing import AsyncGenerator
from database import engine, get_db
from routers.shops import router as shops_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

origins = ["*"]

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
