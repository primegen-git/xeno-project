from fastapi import APIRouter, Request
import json


router = APIRouter()


@router.post("/create")
async def create_customer(req: Request):
    print(req)
    req_msg = json.dumps(req)
    return {"msg", req_msg}
