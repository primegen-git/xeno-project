import os

import models
import requests
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import update
from sqlalchemy.orm import Session
from utils import create_jwt_token

load_dotenv()


router = APIRouter()

scope = "read_products,read_orders,read_customers"

CLIENT_ID = os.getenv("SHOPIFY_API_KEY", None)

if not CLIENT_ID:
    print("client id does not exist")
    raise HTTPException(detail="Client ID is Unknown", status_code=500)

CLIENT_ACCESS_KEY = os.getenv("SHOPIFY_API_SECRET", None)

if not CLIENT_ACCESS_KEY:
    print("access key does not exist")
    raise HTTPException(detail="Client Access Key is Unknown", status_code=500)

BACKEND_URI = os.getenv("BACKEND_URI", None)
if not CLIENT_ACCESS_KEY:
    print("redirect uri does not exist")
    raise HTTPException(detail="Backend URI is Unknown", status_code=500)


@router.get("/install")
async def install(shop: str):
    install_url = (
        f"https://{shop}/admin/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={BACKEND_URI}/shops/callback"
        f"&scope={scope}"
    )

    return RedirectResponse(url=install_url)


@router.get("/callback")
async def callback(req: Request, shop: str, code: str, db: Session = Depends(get_db)):
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_ACCESS_KEY, "code": code}

    try:
        response = requests.post(url=token_url, json=payload)
        response.raise_for_status()
        data = response.json()

        access_token = data.get("access_token")

        user_id = req.cookies.get(shop, None)

        if user_id:
            new_tenant = models.Tenant(shop=shop, access_token=access_token)
            db.add(new_tenant)
            tenant_id = new_tenant.id
            db.execute(
                update(models.User)
                .where(models.User.id == user_id)
                .values(tenant_id=tenant_id)
            )
            db.commit()

            jwt_payload = {"tenant_id": tenant_id}
            encoded_jwt = create_jwt_token(jwt_payload)

            response = JSONResponse(
                content={"success": True, "is_login": False}, status_code=200
            )

            response.set_cookie(
                key="token",
                value=encoded_jwt,
                secure=True,
                samesite="none",
                httponly=True,
            )

            return response

        tenant_id = req.cookies.get("tenant_id", None)

        if not tenant_id:
            raise HTTPException(detail="UnAuthorized access", status_code=401)

        db.execute(
            update(models.Tenant)
            .where(models.Tenant.tenant_id == tenant_id)
            .values(access_token=access_token)
        )

        return JSONResponse(
            content={"success": True, "is_login": True}, status_code=200
        )

    except Exception as e:
        print(f"Callback Error: {e}")
        raise HTTPException(detail="Callback Failed", status_code=500)
