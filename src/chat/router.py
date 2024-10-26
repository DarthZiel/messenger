import json

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends
from requests import Session

from src.chat.queries import create_message
from src.database import get_db

router = APIRouter(
    prefix='/chat',
    tags=['Chat']
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)


            new_message = await create_message(
                db=db,
                user_id=int(message_data["user_id"]),
                message_text=message_data["content"]
            )

            await manager.send_personal_message(f"You wrote: {new_message}", websocket)
            await manager.broadcast(f"Client #{message_data['user_id']} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        #await manager.broadcast(f"Client #{message_data['user_id']} left the chat")
