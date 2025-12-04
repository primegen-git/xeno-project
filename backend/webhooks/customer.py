from fastapi import APIRouter, Request


router = APIRouter()


@router.post("/create")
async def create_customer(req: Request):
    body = await req.json()
    print(body)
    return {"status", True}
