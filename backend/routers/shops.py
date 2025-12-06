import os

import models
import requests
from database import get_db
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import delete, update
from sqlalchemy.orm import Session
from utils import create_jwt_token, decode_jwt_token

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

REDIRECT_URI = os.getenv("REDIRECT_URI", None)
if not CLIENT_ACCESS_KEY:
    print("redirect uri does not exist")
    raise HTTPException(detail="REDIRECT URI is Unknown", status_code=500)


@router.get("/install")
async def install(shop: str, user_id=None):
    install_url = (
        f"https://{shop}/admin/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}/shops/callback"
        f"&scope={scope}"
        f"&state={user_id}"
    )

    return RedirectResponse(url=install_url)


@router.get("/callback")
async def callback(
    req: Request, shop: str, code: str, state=None, db: Session = Depends(get_db)
):
    token_url = f"https://{shop}/admin/oauth/access_token"
    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_ACCESS_KEY, "code": code}

    try:
        response = requests.post(url=token_url, json=payload)
        response.raise_for_status()
        data = response.json()

        access_token = data.get("access_token")

        if state:
            new_tenant = models.Tenant(shop=shop, access_token=access_token)
            db.add(new_tenant)
            db.commit()
            tenant_id = new_tenant.id
            db.execute(
                update(models.User)
                .where(models.User.id == state)
                .values(tenant_id=tenant_id)
            )
            db.commit()

            jwt_payload = {"tenant_id": tenant_id}
            encoded_jwt = create_jwt_token(jwt_payload)

            response = JSONResponse(
                content={"success": True, "is_login": False}, status_code=200
            )

            response.delete_cookie(shop)

            response.set_cookie(
                key="token",
                value=encoded_jwt,
                secure=True,
                samesite="none",
                httponly=True,
            )

            return response

        encoded_jwt = req.cookies.get("token", None)

        if not encoded_jwt:
            raise HTTPException(detail="UnAuthorized access", status_code=401)

        tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

        if not tenant_id:
            raise HTTPException(detail="UnAuthorized access", status_code=401)

        db.execute(
            update(models.Tenant)
            .where(models.Tenant.id == tenant_id)
            .values(access_token=access_token)
        )

        return JSONResponse(
            content={"success": True, "is_login": True}, status_code=200
        )

    except Exception as e:
        print(f"Callback Error: {e}")
        db.execute(delete(models.User).where(models.User.id == state))
        db.commit()
        raise HTTPException(detail="Callback Failed", status_code=500)
