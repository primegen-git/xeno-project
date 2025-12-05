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
        db_customer = db.get(models.Customer, customer.id)

        if db_customer:
            db_customer.first_name = customer.first_name
            db_customer.last_name = customer.last_name
            db_customer.email = customer.email
            db_customer.verified_email = customer.verified_email
            db_customer.tenant_id = tenant_id

            db_customer.addresses.clear()
            for addr in customer.addresses:
                db_customer.addresses.append(
                    models.Address(
                        id=addr.id,
                        address1=addr.address1,
                        city=addr.city,
                        province=addr.province,
                        zip=addr.zip,
                        country=addr.country,
                    )
                )
        else:
            customer_model = models.Customer(
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

            db.add(customer_model)

    db.commit()

    return Response(content="Customers Sync Successfully", status_code=200)


@router.get("/products")
async def get_products(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id(req)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    products = fetch_data_from_shopify(shop, "products", access_token)

    for product in products:
        db_product = db.get(models.Product, product.id)

        if db_product:
            db_product.id = product.id
            db_product.title = product.title
            db_product.vendor = product.vendor
            db_product.product_type = product.product_type
            db_product.tags = product.tags
            db_product.tenant_id = tenant_id

            db_product.variants.clear()

            for variant in product.variants:
                db_product.variants.append(
                    models.Variant(
                        id=variant.id,
                        option1=variant.option1,
                        price=variant.price,
                        sku=variant.sku,
                        inventory_quantity=variant.inventory_quantity,
                    )
                )

        else:
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

    return Response(content="Product Sync Successfully", status_code=200)


@router.get("/orders")
async def get_orders(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id(req)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    orders = fetch_data_from_shopify(shop, "orders", access_token)

    for order in orders:
        db_order = db.get(models.Order, order.id)

        if db_order:
            db_order.tenant_id = tenant_id
            db_order.customer_id = order.customer.id
            db_order.variant_id = order.line_items[0].variant_id

        else:
            order_model = models.Order(
                id=order.id,
                tenant_id=tenant_id,
                customer_id=order.customer.id,
                variant_id=order.line_items[0].variant_id,
            )

            db.add(order_model)

    db.commit()

    return Response(content="Orders Sync Successfully", status_code=200)
