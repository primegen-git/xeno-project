import os
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, Depends, Response
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from sqlalchemy import Select
from sqlalchemy.orm import Session
from database import get_db
import requests
import models
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
async def install(res: Response, shop: str, db: Session = Depends(get_db)):
    # tenant = db.execute(
    #     Select(models.Tenant).where(models.Tenant.shop == shop)
    # ).scalar_one_or_none()
    #
    # if tenant is not None:
    #     payload = {"tenant_id": tenant.id, "access_token": tenant.access_token}
    #
    #     encoded_jwt = create_jwt_token(payload)
    #
    #     res.set_cookie(key="token", value=encoded_jwt, httponly=True)
    #
    #     return {"success": True, "message": "Login Successful"}

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

        access_token = data.get("access_token")
        granted_scopes = data.get("scope")  # Check what scopes Shopify actually gave us

        print(f"✅ NEW TOKEN RECEIVED FOR {shop}")
        print(f"🔎 Scopes on this token: {granted_scopes}")

        # --- FIX: UPSERT LOGIC (Update or Insert) ---
        existing_tenant = db.execute(
            Select(models.Tenant).where(models.Tenant.shop == shop)
        ).scalar_one_or_none()

        if existing_tenant:
            # UPDATE the existing row with the NEW token
            print("🔄 Updating existing tenant token...")
            existing_tenant.access_token = access_token
            # If you have a scope column, update it too
            # existing_tenant.scopes = granted_scopes
            tenant_id = existing_tenant.id
        else:
            # INSERT a new row
            print("kj Creating new tenant...")
            new_tenant = models.Tenant(shop=shop, access_token=access_token)
            db.add(new_tenant)
            db.commit()  # Commit to generate the ID
            db.refresh(new_tenant)
            tenant_id = new_tenant.id

        db.commit()  # Save changes

        # Generate JWT with the NEW token
        jwt_payload = {"tenant_id": tenant_id, "access_token": access_token}
        encoded_jwt = create_jwt_token(jwt_payload)
        res.set_cookie(key="token", value=encoded_jwt, httponly=True)

        return {"success": True, "message": "App Re-installed & Token Updated"}

    except Exception as e:
        print(f"Callback Error: {e}")
        raise HTTPException(detail="Callback Failed", status_code=500)
