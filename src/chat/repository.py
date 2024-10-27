from http.client import HTTPException

from sqlalchemy import select, and_, or_

from src.chat.models import Chat
from src.auth.models import User
from src.auth.schemas import UserRead
from src.database import SessionLocal
from src.chat.schemas import GetChatByEmail


class ChatRepository:
    @staticmethod
    async def get_user(data):
        async with SessionLocal() as session:
            query = select(User.id).where(User.email == data)
            result = await session.execute(query)
            user_models = result.scalar_one_or_none()
            return user_models

    @staticmethod
    async def get_chat(participants):
        async with SessionLocal() as session:
            query = select(Chat).where(or_(
                and_(Chat.participant_one_id == participants.participant_one,
                     Chat.participant_two_id == participants.participant_two),
                and_(Chat.participant_one_id == participants.participant_two,
                     Chat.participant_two_id == participants.participant_one)
            ))
            result = await session.execute(query)
            chat_model = result.scalar_one_or_none()
            return chat_model

    @staticmethod
    async def set_chat(participants):
        async with SessionLocal() as session:
            new_chat = Chat(participant_one_id=participants.participant_one,
                            participant_two_id=participants.participant_two)
            session.add(new_chat)

            try:
                await session.commit()
                await session.refresh(new_chat)
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=400, detail=str(e))
