import asyncio
from typing import Dict, List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Map tenant_id to a list of queues (one per connected client)
        self.active_connections: Dict[int, List[asyncio.Queue]] = {}

    async def connect(self, tenant_id: int) -> asyncio.Queue:
        queue = asyncio.Queue()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(queue)
        return queue

    def disconnect(self, tenant_id: int, queue: asyncio.Queue):
        if tenant_id in self.active_connections:
            if queue in self.active_connections[tenant_id]:
                self.active_connections[tenant_id].remove(queue)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]

    async def broadcast(self, tenant_id: int, message: str):
        if tenant_id in self.active_connections:
            for queue in self.active_connections[tenant_id]:
                await queue.put(message)


manager = ConnectionManager()
