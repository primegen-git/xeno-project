from fastapi import APIRouter, Request
import json


router = APIRouter()


@router.post("/create")
async def create_customer(req: Request):
    print(req)
    return {"msg", "customer_create_request"}
