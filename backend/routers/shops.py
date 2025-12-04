import os
import sys
from fastapi import APIRouter, Depends, Response
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import requests
import models
from utils import create_jwt_token


load_dotenv()


router = APIRouter()

scope = "read_products, read_orders, read_customers"

CLIENT_ID = os.getenv("SHOPIFY_API_KEY", None)

if not CLIENT_ID:
    print("client id does not exist")
    sys.exit(1)

CLIENT_ACCESS_KEY = os.getenv("SHOPIFY_API_SECRET", None)

if not CLIENT_ACCESS_KEY:
    print("access key does not exist")
    sys.exit(1)

BACKEND_URI = os.getenv("BACKEND_URI", None)
if not CLIENT_ACCESS_KEY:
    print("redirect uri does not exist")
    sys.exit(1)


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
async def callback(res: Response, shop: str, code: str, db: Session = Depends(get_db)):
    token_url = f"https://{shop}/admin/oauth/access_token"

    payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_ACCESS_KEY, "code": code}

    try:
        response = requests.post(url=token_url, json=payload)

        response.raise_for_status()

        data = response.json()

        if "access_token" not in data:
            raise Exception("does not get the access token in response")

        access_token = data["access_token"]

        tenant_model = models.Tenant(shop=shop, access_token=access_token)

        db.add(tenant_model)
        db.commit()
        db.refresh(tenant_model)

        jwt_payload = {"tenant_id": tenant_model.id}

        encoded_jwt = create_jwt_token(jwt_payload)

        res.set_cookie(key="token", value=encoded_jwt)

        return {"success": True}

    except Exception as e:
        print(f"some error occurs in callback\nerror: {e}")
        sys.exit(1)
