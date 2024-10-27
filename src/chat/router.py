import json

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
from src.chat.services import validate_token
from requests import Session


from src.chat.schemas import Participants
from src.chat.repository import ChatRepository
from src.chat.queries import create_message
from src.database import get_db
from src.chat.schemas import GetChatByEmail

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
        # await manager.broadcast(f"Client #{message_data['user_id']} left the chat")


@router.get('/{email}')
async def get_user(email: str):
    user_id = await ChatRepository.get_user(data=email)

    if user_id is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    return {'id': user_id}


@router.get('/{participant_one}/{participant_two}')
async def get_chat(participant_one: int, participant_two: int):
    participants = Participants(participant_one=participant_one, participant_two=participant_two)
    data = await ChatRepository.get_chat(participants)
    if data is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {'data': data}


@router.post('/{participant_one}/{participant_two}')
async def set_chat(participant_one: int, participant_two: int):
    participants = Participants(participant_one=participant_one, participant_two=participant_two)
    existing_chat = await ChatRepository.get_chat(participants)

    if existing_chat:
        raise HTTPException(status_code=400, detail="Chat already exists")
    data = await ChatRepository.set_chat(participants)
    return {'data': data}






@router.websocket("/ws/{token}")
async def chat_websocket(websocket: WebSocket, token: str):
    # Проверка токена
    payload = validate_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid token")

    user_id = payload.get("sub")  # Получаем идентификатор пользователя из полезной нагрузки

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            new_message = await create_message(
                db=Depends(get_db),
                user_id=int(user_id),  # Используем user_id из токена
                message_text=message_data["content"]
            )

            await manager.send_personal_message(f"You wrote: {new_message}", websocket)
            await manager.broadcast(f"Client #{user_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{user_id} left the chat")