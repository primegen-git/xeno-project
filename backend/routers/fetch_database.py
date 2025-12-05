from collections import defaultdict
from fastapi import APIRouter, Depends, Request, Query
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from utils import decode_jwt_token
from database import get_db
import models
from datetime import date, datetime, timezone, time

router = APIRouter()


def get_tenent_id_and_access_token(req):
    encoded_jwt_token = req.cookies.get("token", None)
    if encoded_jwt_token is None:
        raise HTTPException(status_code=401, detail="User is unauthorized.")

    payload = decode_jwt_token(encoded_jwt_token)

    tenant_id = payload["tenant_id"]

    access_token = payload["access_token"]

    return (tenant_id, access_token)


@router.get("/total_customers")
async def get_total_customers(req: Request, db: Session = Depends(get_db)):
    tenant_id, _ = get_tenent_id_and_access_token(req)

    total_customers = db.scalar(
        select(func.count(models.Customer.id)).where(
            models.Customer.tenant_id == tenant_id
        )
    )

    return JSONResponse(content=total_customers, status_code=200)


@router.get("/total_products")
async def get_total_products(req: Request, db: Session = Depends(get_db)):
    tenant_id, _ = get_tenent_id_and_access_token(req)

    total_products = db.scalar(
        select(func.count(models.Product.id)).where(
            models.Product.tenant_id == tenant_id
        )
    )
    return JSONResponse(content=total_products, status_code=200)


@router.get("/total_orders")
async def get_total_orders(req: Request, db: Session = Depends(get_db)):
    tenant_id, _ = get_tenent_id_and_access_token(req)

    total_orders = db.scalar(
        select(func.count(models.Order.id)).where(models.Order.tenant_id == tenant_id)
    )

    return JSONResponse(content=total_orders, status_code=200)


@router.get("/top_customers")
async def get_top_customers(req: Request, db: Session = Depends(get_db)):
    tenant_id, _ = get_tenent_id_and_access_token(req)

    stmt = (
        select(
            func.sum((models.Order.quantity * models.Variant.price)).label(
                "total_price"
            ),
            func.sum((models.Order.quantity)).label("total_quantity"),
            (models.Order.customer_id),
        )
        .join(models.Variant, (models.Order.variant_id == models.Variant.id))
        .where(models.Order.tenant_id == tenant_id)
        .group_by(models.Order.customer_id)
        .order_by(desc("total_price"))
        .limit(5)
    )

    results = db.execute(stmt).all()

    response = defaultdict(list)

    for total_price, total_quantity, customer_id in results:
        customer_model = db.get(models.Customer, customer_id)

        if not customer_model:
            continue

        response["data"].append(
            {
                "first_name": customer_model.first_name,
                "last_name": customer_model.last_name,
                "email": customer_model.email,
                "total_price": total_price,
                "total_quantity": total_quantity,
            }
        )

    return JSONResponse(content=response, status_code=200)


@router.get("/orders")
def list_orders(
    req: Request,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    tenant_id, _ = get_tenent_id_and_access_token(req)
    stmt = select(models.Order).where(models.Order.tenant_id == tenant_id)

    if start_date:
        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        stmt = stmt.where(models.Order.created_at >= start_dt)

    if end_date:
        end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        stmt = stmt.where(models.Order.created_at <= end_dt)

    orders = db.scalars(stmt).all()
    return orders
