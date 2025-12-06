import models
from database import get_db
from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from utils import create_jwt_token, get_hashed_password

router = APIRouter()


class SignUPModel(BaseModel):
    shop: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(payload: SignUPModel, db: Session = Depends(get_db)):
    existing_model = db.execute(
        select(models.User).where(models.User.email == payload.email)
    ).scalar_one_or_none()

    if existing_model:
        raise HTTPException(status_code=409, detail="Account Already exist")

    existing_model = db.execute(
        select(models.Tenant).where(models.Tenant.shop == payload.shop)
    ).scalar_one_or_none()

    if existing_model:
        raise HTTPException(status_code=409, detail="Shop Already exist")

    user_model = models.User(
        email=payload.email, hashed_password=get_hashed_password(payload.password)
    )

    db.add(user_model)
    db.commit()

    return JSONResponse(
        content={"success": True, "shop": payload.shop, "user_id": user_model.id},
        status_code=200,
    )


@router.post("/login")
async def login(payload: LoginModel, db: Session = Depends(get_db)):
    existing_user = db.execute(
        select(models.User).where(models.User.email == payload.email)
    ).scalar_one_or_none()

    if not existing_user:
        raise HTTPException(detail="User does not exist", status_code=404)

    hashed_password = get_hashed_password(payload.password)

    if existing_user.hashed_password != hashed_password:
        raise HTTPException(detail="Password does not match", status_code=401)

    shop = existing_user.tenant.shop
    tenant_id = existing_user.tenant_id

    response = JSONResponse(content={"success": True, "shop": shop}, status_code=200)

    encoded_jwt = create_jwt_token({"tenant_id": tenant_id})

    response.set_cookie(
        key="token", value=encoded_jwt, secure=True, samesite="none", httponly=True
    )

    return response


@router.get("/logout")
async def logout(res: Response):
    res.delete_cookie(key="token")
    return JSONResponse(content="logout successfully", status_code=200)
