from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException
from utils import fetch_data_from_shopify, get_tenant_id_and_access_token
import models
from sqlalchemy.orm import Session
from database import get_db
from datetime import timezone


router = APIRouter()


@router.get("/customers")
async def get_customers(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id_and_access_token(req, db)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    customers = fetch_data_from_shopify(shop, "customers", access_token)

    try:
        for customer in customers:
            db_customer = db.get(models.Customer, customer.id)

            if db_customer:
                db_customer.first_name = customer.first_name
                db_customer.last_name = customer.last_name
                db_customer.email = customer.email
                db_customer.verified_email = customer.verified_email
                db_customer.tenant_id = tenant_id
                db_customer.address = models.Address(
                    id=customer.default_address.id,
                    address1=customer.default_address.address1,
                    city=customer.default_address.city,
                    zip=customer.default_address.zip,
                    country=customer.default_address.country,
                    province=customer.default_address.province,
                )

            else:
                customer_model = models.Customer(
                    id=customer.id,
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    email=customer.email,
                    verified_email=customer.verified_email,
                    tenant_id=tenant_id,
                    address=models.Address(
                        id=customer.default_address.id,
                        address1=customer.default_address.address1,
                        city=customer.default_address.city,
                        zip=customer.default_address.zip,
                        country=customer.default_address.country,
                        province=customer.default_address.province,
                    ),
                )

                db.add(customer_model)

        db.commit()

        return Response(content="Customers Sync Successfully", status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in saving customers data to database\nError: {e}",
        )


@router.get("/products")
async def get_products(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id_and_access_token(req, db)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    products = fetch_data_from_shopify(shop, "products", access_token)

    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in saving products data to database\nError: {e}",
        )


@router.get("/orders")
async def get_orders(req: Request, shop: str, db: Session = Depends(get_db)):
    tenant_id, access_token = get_tenant_id_and_access_token(req, db)

    if tenant_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error.")

    orders = fetch_data_from_shopify(shop, "orders", access_token)

    try:
        for order in orders:
            db_order = db.get(models.Order, order.id)

            if db_order:
                db_order.tenant_id = tenant_id
                db_order.customer_id = order.customer.id
                db_order.variant_id = order.line_items[0].variant_id
                db_order.created_at = order.created_at.astimezone(timezone.utc)
                db_order.quantity = order.line_items[0].quantity

            else:
                order_model = models.Order(
                    id=order.id,
                    tenant_id=tenant_id,
                    customer_id=order.customer.id,
                    variant_id=order.line_items[0].variant_id,
                    created_at=order.created_at.astimezone(timezone.utc),
                    quantity=order.line_items[0].quantity,
                )

                db.add(order_model)

        db.commit()

        return Response(content="Orders Sync Successfully", status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in saving orders data to database\nError: {e}",
        )
