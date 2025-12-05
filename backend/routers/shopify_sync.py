from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from utils import fetch_data_from_shopify, decode_jwt_token
import models
from sqlalchemy.orm import Session
from database import get_db


router = APIRouter()


def get_tenant_id(req):
    encoded_jwt_token = req.cookies.get("token", None)
    if encoded_jwt_token is None:
        raise HTTPException(status_code=401, detail="User is unauthorized.")

    payload = decode_jwt_token(encoded_jwt_token)

    tenant_id = payload["tenant_id"]

    access_token = payload["access_token"]

    return (tenant_id, access_token)


@router.get("/customers")
async def get_customers(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id(req)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    customers = fetch_data_from_shopify(shop, "customers", access_token)

    for customer in customers:
        customer_models = models.Customer(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            verified_email=customer.verified_email,
            tenant_id=tenant_id,
            addresses=[
                models.Address(
                    id=addr.id,
                    address1=addr.address1,
                    city=addr.city,
                    zip=addr.zip,
                    country=addr.country,
                    province=addr.province,
                )
                for addr in customer.addresses
            ],
        )

        db.add(customer_models)

    db.commit()

    return Response(content="Customers Sync Successfully", status_code=200)
