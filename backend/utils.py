import os
import time
from typing import Dict
import jwt
from dotenv import load_dotenv
import requests
from sqlalchemy import Select
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.exceptions import HTTPException
from database import get_db
import models
from pydantic_models import CustomerResponse


load_dotenv()


JWT_SECRET = os.getenv("JWT_SECRET", None)

if JWT_SECRET is None:
    print("jwt secret does not exist")
    raise HTTPException(detail="JWT Secret is Unknown", status_code=500)


JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", None)

if JWT_ALGORITHM is None:
    print("jwt algorithm does not exist")
    raise HTTPException(detail="JWT Algorithm is Unknown", status_code=500)


def create_jwt_token(payload: Dict):
    encoded_jwt = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(encoded_jwt):
    payload = jwt.decode(encoded_jwt, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
    return payload


def get_access_token(shop, db: Session = Depends(get_db)):
    access_token = db.execute(
        Select(models.Tenant.access_token).where(models.Tenant.shop == shop)
    ).scalar_one_or_none

    if access_token is None:
        raise HTTPException(status_code=401, detail="access token does not exist")

    return access_token


def fetch_data_from_shopify(shop, resource, access_token):
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token,
    }

    url = f"https://{shop}/admin/api/2024-10/{resource}.json"

    shopify_data = []

    while url:
        try:
            response = requests.get(url=url, headers=headers)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"429 too many request, retry_after : {retry_after}")
                time.sleep(retry_after)
                continue

            response.raise_for_status()

            data = response.json()

            parsed_data = []
            if resource == "customers":
                parsed_data = CustomerResponse(**data)

            shopify_data.extend(parsed_data.customers)

            if "link" in response.headers:
                parts = response.headers["link"].split(",")

                for part in parts:
                    section = part.split(";")

                    if "next" in section[-1]:
                        idx1 = section[0].find("<")
                        idx2 = section[0].find(">")
                        url = section[0][idx1 + 1 : idx2]
            else:
                url = None

        except Exception as e:
            print("Error occurs during customer data sync from shopify")
            print(f"Error : {e}")
            raise HTTPException(
                detail="Error Occur in customer sync process from shopify",
                status_code=500,
            )

    return shopify_data
