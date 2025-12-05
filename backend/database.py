import os
from fastapi.exceptions import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from dotenv import load_dotenv

load_dotenv()

DATABASE_USER = os.getenv("POSTGRES_USER", None)

if DATABASE_USER is None:
    print("DATABASE USER IS UNKNOWN")
    raise HTTPException(detail="Database user does not exist", status_code=500)


DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD", None)

if DATABASE_PASSWORD is None:
    print("DATABASE PASSWORD IS UNKNOWN")
    raise HTTPException(detail="Database Password does not exist", status_code=500)

DATABASE_HOST = os.getenv("POSTGRES_HOST", None)

if DATABASE_HOST is None:
    print("DATABASE HOST IS UNKNOWN")
    raise HTTPException(detail="Database Host does not exist", status_code=500)


DATABASE_PORT = os.getenv("POSTGRES_PORT", None)

if DATABASE_PORT is None:
    print("DATABASE PORT IS UNKNOWN")
    raise HTTPException(detail="Database Port does not exist", status_code=500)


DATABASE_NAME = os.getenv("POSTGRES_DATABASE_NAME", None)

if DATABASE_NAME is None:
    print("DATABASE NAME IS UNKNOWN")
    raise HTTPException(detail="Database Name does not exist", status_code=500)


DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{int(DATABASE_PORT)}/{DATABASE_NAME}"


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
