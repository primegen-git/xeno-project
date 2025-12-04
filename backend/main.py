from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from typing import AsyncGenerator
from database import SessionLocal, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


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
