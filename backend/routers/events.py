from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from utils import decode_jwt_token
from connection_manager import manager
import asyncio
from fastapi.exceptions import HTTPException

router = APIRouter()

@router.get("/events")
async def sse_endpoint(req: Request):
    encoded_jwt = req.cookies.get("token", None)
    if not encoded_jwt:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = decode_jwt_token(encoded_jwt)
        tenant_id = payload.get("tenant_id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Token")

    if not tenant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async def event_generator():
        queue = await manager.connect(tenant_id)
        try:
            while True:
                # Wait for a message from the queue
                message = await queue.get()
                # Yield it in SSE format
                yield f"data: {message}\n\n"
        except asyncio.CancelledError:
            manager.disconnect(tenant_id, queue)
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")
