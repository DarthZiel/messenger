import json
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException

from src.chat.schemas import Participants
from src.chat.repository import ChatRepository
from src.history.repository import HistoryRepository
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






@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            chat_id = int(message_data.get("chat_id"))
            user_id = int(message_data.get("user_id"))
            content = message_data.get("content")
            user = await ChatRepository.get_user_by_id(user_id)
            await HistoryRepository.write_message(
                db=db,
                user_id=user_id,
                chat_id=chat_id,
                message_text=content
            )

            # Отправка личного сообщения пользователю, подтвердив сохранение
            # await manager.send_personal_message(f"You wrote: {content}", websocket)
            # # Отправка сообщения всем пользователям о новом сообщении
            await manager.broadcast(f"{user}: {content}")
    except WebSocketDisconnect:
        # Обработка отключения WebSocket и удаление пользователя из менеджера
        await manager.disconnect(websocket)
        # Неиспользуемый `message_data` не вызывает ошибку при отключении
        await manager.broadcast(f"{user} покинул чат")