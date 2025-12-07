import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
import requests

from database import get_db
import models
from pydantic_models import CustomerModel, OrderModel, ProductModel
from utils import decode_jwt_token, verify_webhook
import json

router = APIRouter()

load_dotenv()


BACKEND_URI = os.getenv("BACKEND_URI", None)

if not BACKEND_URI:
    raise HTTPException(detail="BACKEND_URI does not exist", status_code=500)


def delete_webhook(req, db, resource):
    encoded_jwt = req.cookies.get("token", None)
    tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    webhook_model = db.execute(
        select(models.Webhook)  # Select the whole model
        .where(models.Webhook.tenant_id == tenant_id)
        .where(models.Webhook.topic == f"{resource}/create")
    ).scalar_one_or_none()

    tenant_model = db.get(models.Tenant, tenant_id)

    if not tenant_model:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not webhook_model:
        return JSONResponse(
            status_code=200, content={"message": "Webhook not found in DB"}
        )

    url = f"https://{tenant_model.shop}/admin/api/2024-10/webhooks/{webhook_model.id}.json"

    headers = {
        "X-Shopify-Access-Token": tenant_model.access_token,
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200 or response.status_code == 404:
        db.delete(webhook_model)
        db.commit()
        return response

    return response


@router.get("/check")
async def check_webhook_exist(req: Request, db: Session = Depends(get_db)):
    encoded_jwt = req.cookies.get("token", None)

    if not encoded_jwt:
        raise HTTPException(status_code=401, detail="Unauthorized")

    tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    content = {}

    webhooks = db.scalars(
        select(models.Webhook).where(models.Webhook.tenant_id == tenant_id)
    ).all()

    for webhook in webhooks:
        if webhook.topic == "orders/create":
            content["orders"] = True
        elif webhook.topic == "products/create":
            content["products"] = True
        elif webhook.topic == "customers/create":
            content["customers"] = True

    return JSONResponse(content=content, status_code=200)


@router.get("/register/order/create")
async def register_order_webhook(req: Request, db: Session = Depends(get_db)):
    try:
        encoded_jwt = req.cookies.get("token", None)

        if not encoded_jwt:
            raise HTTPException(status_code=401, detail="Unauthorize")

        tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

        if not tenant_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        tenant_model = db.execute(
            select(models.Tenant).where(models.Tenant.id == tenant_id)
        ).scalar_one()

        url = f"https://{tenant_model.shop}/admin/api/2024-10/webhooks.json"

        payload = {
            "webhook": {
                "topic": "orders/create",
                "address": f"https://{BACKEND_URI}/webhooks/orders/create",
                "format": "json",
            }
        }

        headers = {
            "X-Shopify-Access-Token": tenant_model.access_token,
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            body = response.json()["webhook"]

            webhook_model = models.Webhook(
                id=body["id"],
                topic=body["topic"],
                created_at=body["created_at"],
                format=body["format"],
                tenant_id=tenant_id,
            )

            db.add(webhook_model)
            db.commit()

            return JSONResponse(
                content={"success": True, "message": "Order created webhooks"},
                status_code=200,
            )
        if response.status_code == 422:
            return JSONResponse(
                content={"success": True, "message": "Webhook already exist"},
                status_code=409,
            )
        response.raise_for_status()
    except Exception as e:
        print(f"Error occurs in order create webhook\nError : {e}")
        raise HTTPException(status_code=500)


@router.get("/register/customer/create")
async def register_customer_webhook(req: Request, db: Session = Depends(get_db)):
    try:
        encoded_jwt = req.cookies.get("token", None)

        if not encoded_jwt:
            raise HTTPException(status_code=401, detail="UnAuthorize")

        tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

        if not tenant_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        tenant_model = db.execute(
            select(models.Tenant).where(models.Tenant.id == tenant_id)
        ).scalar_one()

        url = f"https://{tenant_model.shop}/admin/api/2024-10/webhooks.json"

        payload = {
            "webhook": {
                "topic": "customers/create",
                "address": f"https://{BACKEND_URI}/webhooks/customers/create",
                "format": "json",
            }
        }

        headers = {
            "X-Shopify-Access-Token": tenant_model.access_token,
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            body = response.json()["webhook"]

            webhook_model = models.Webhook(
                id=body["id"],
                topic=body["topic"],
                created_at=body["created_at"],
                format=body["format"],
                tenant_id=tenant_id,
            )

            db.add(webhook_model)
            db.commit()
            return JSONResponse(
                content={"success": True, "message": "Customer created webhooks"},
                status_code=200,
            )
        if response.status_code == 422:
            return JSONResponse(
                content={"success": True, "message": "Webhook already exist"},
                status_code=200,
            )
        response.raise_for_status()
    except Exception as e:
        print(f"Error occurs in Customer create webhook\nError : {e}")
        raise HTTPException(status_code=500)


@router.get("/register/product/create")
async def register_product_webhook(req: Request, db: Session = Depends(get_db)):
    try:
        encoded_jwt = req.cookies.get("token", None)

        if not encoded_jwt:
            raise HTTPException(status_code=401, detail="UnAuthorize")

        tenant_id = decode_jwt_token(encoded_jwt=encoded_jwt).get("tenant_id", None)

        if not tenant_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        tenant_model = db.execute(
            select(models.Tenant).where(models.Tenant.id == tenant_id)
        ).scalar_one()

        url = f"https://{tenant_model.shop}/admin/api/2024-10/webhooks.json"

        payload = {
            "webhook": {
                "topic": "products/create",
                "address": f"https://{BACKEND_URI}/webhooks/products/create",
                "format": "json",
            }
        }

        headers = {
            "X-Shopify-Access-Token": tenant_model.access_token,
            "Content-Type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 201:
            body = response.json()["webhook"]

            webhook_model = models.Webhook(
                id=body["id"],
                topic=body["topic"],
                created_at=body["created_at"],
                format=body["format"],
                tenant_id=tenant_id,
            )

            db.add(webhook_model)
            db.commit()

            return JSONResponse(
                content={"success": True, "message": "Product created webhooks"},
                status_code=200,
            )
        if response.status_code == 422:
            return JSONResponse(
                content={"success": True, "message": "Webhook already exist"},
                status_code=200,
            )
        response.raise_for_status()
    except Exception as e:
        print(f"Error occurs in Product create webhook\nError : {e}")
        raise HTTPException(status_code=500)


@router.post("/orders/create")
async def save_order(req: Request, db: Session = Depends(get_db)):
    hmac_header = req.headers.get("X-Shopify-Hmac-Sha256", None)

    if not hmac_header:
        return
    body = await req.body()

    if not verify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Unauthorized Webhook")

    data = json.loads(body)
    order = OrderModel(**data)

    shop = req.headers.get("X-Shopify-Shop-Domain", None)

    if not shop:
        return

    tenant_id = db.execute(
        select(models.Tenant.id).where(models.Tenant.shop == shop)
    ).scalar_one_or_none()

    if not tenant_id:
        return

    existing_order = db.execute(
        select(models.Order).where(models.Order.id == order.id)
    ).scalar_one_or_none()

    if existing_order:
        print(f"Order {order.id} already exists. Skipping.")
        return

    order_model = models.Order(
        id=order.id,
        tenant_id=tenant_id,
        customer_id=order.customer.id,
        variant_id=order.line_items[0].variant_id,
        quantity=order.line_items[0].quantity,
        created_at=order.created_at,
    )

    db.add(order_model)
    db.commit()


@router.post("/products/create")
async def save_product(req: Request, db: Session = Depends(get_db)):
    hmac_header = req.headers.get("X-Shopify-Hmac-Sha256", None)

    if not hmac_header:
        return

    body = await req.body()

    if not verify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Unauthorized Webhook")

    data = json.loads(body)
    product = ProductModel(**data)

    shop = req.headers.get("X-Shopify-Shop-Domain", None)

    if not shop:
        return

    tenant_id = db.execute(
        select(models.Tenant.id).where(models.Tenant.shop == shop)
    ).scalar_one_or_none()

    if not tenant_id:
        return

    existing_product = db.execute(
        select(models.Product).where(models.Product.id == product.id)
    ).scalar_one_or_none()

    if existing_product:
        print(f"Product {product.id} already exists. Skipping.")
        return

    product_model = models.Product(
        id=product.id,
        title=product.title,
        vendor=product.vendor,
        product_type=product.product_type,
        tags=product.tags,
        tenant_id=tenant_id,
        variants=[
            models.Variant(
                id=variant.id,
                option1=variant.option1,
                price=variant.price,
                sku=variant.sku,
                inventory_quantity=variant.inventory_quantity,
            )
            for variant in product.variants
        ],
    )

    db.add(product_model)
    db.commit()


@router.post("/customers/create")
async def customer_product(req: Request, db: Session = Depends(get_db)):
    hmac_header = req.headers.get("X-Shopify-Hmac-Sha256", None)

    if not hmac_header:
        return
    body = await req.body()

    if not verify_webhook(body, hmac_header):
        raise HTTPException(status_code=401, detail="Unauthorized Webhook")

    data = json.loads(body)
    customer = CustomerModel(**data)

    shop = req.headers.get("X-Shopify-Shop-Domain", None)

    if not shop:
        return

    tenant_id = db.execute(
        select(models.Tenant.id).where(models.Tenant.shop == shop)
    ).scalar_one_or_none()

    if not tenant_id:
        return

    existing_customer = db.execute(
        select(models.Customer).where(models.Customer.id == customer.id)
    ).scalar_one_or_none()

    if existing_customer:
        print(f"Customer {customer.id} already exists. Skipping.")
        return

    address_model = None
    if customer.default_address:
        address_model = models.Address(
            id=customer.default_address.id,
            address1=customer.default_address.address1,
            city=customer.default_address.city,
            zip=customer.default_address.zip,
            country=customer.default_address.country,
            province=customer.default_address.province,
        )

    customer_model = models.Customer(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        verified_email=customer.verified_email,
        tenant_id=tenant_id,
        address=address_model,
    )

    db.add(customer_model)
    db.commit()


@router.delete("/order")
async def delete_order_webhook(req: Request, db: Session = Depends(get_db)):
    response = delete_webhook(req, db, "orders")

    if response.status_code == 200:
        return JSONResponse(
            content={"success": True, "message": "order created webhook deleted"}
        )

    else:
        return JSONResponse(status_code=response.status_code, content=response.json())


@router.delete("/product")
async def delete_product_webhook(req: Request, db: Session = Depends(get_db)):
    response = delete_webhook(req, db, "products")

    if response.status_code in (200, 204):
        return JSONResponse(
            content={"success": True, "message": "Product webhook deleted"},
            status_code=200,
        )

    try:
        error_body = response.json()
    except Exception:
        error_body = {"error": "Unknown error from Shopify"}

    return JSONResponse(status_code=response.status_code, content=error_body)


@router.delete("/customer")
async def delete_customer_webhook(req: Request, db: Session = Depends(get_db)):
    response = delete_webhook(req, db, "customers")

    if response.status_code in (200, 204):
        return JSONResponse(
            content={"success": True, "message": "Customer webhook deleted"},
            status_code=200,
        )

    try:
        error_body = response.json()
    except Exception:
        error_body = {"error": "Unknown error from Shopify"}

    return JSONResponse(status_code=response.status_code, content=error_body)
