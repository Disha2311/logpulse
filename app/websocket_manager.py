from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept connection and add to active pool."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove connection from active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message to all active WebSocket clients."""
        # Create a copy of the list to avoid modification during iteration
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                # If sending fails, clean up the stale connection
                self.disconnect(connection)

# Global instance
manager = ConnectionManager()
