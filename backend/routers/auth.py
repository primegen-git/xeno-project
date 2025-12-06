from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
import models
from utils import hashed_password

router = APIRouter()


class SignUPModel(BaseModel):
    shop: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str


@router.post("signup/")
async def signup(payload: SignUPModel, db: Session = Depends(get_db)):
    existing_model = db.execute(
        select(models.Tenant).where(models.Tenant.shop == payload.shop)
    ).scalar_one_or_none()

    if existing_model:
        raise HTTPException(status_code=409, detail="Account Already exist")

    user_model = models.User(
        email=payload.email, hashed_passwrod=hashed_password(payload.password)
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    response = JSONResponse(
        content={"success": True, "shop": payload.shop}, status_code=200
    )
    response.set_cookie(
        key=payload.shop,
        value=user_model.shop,
        secure=True,
        samesite="none",
        httponly=True,
    )

    return response
