from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, Integer, DateTime, MetaData, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship

from src.database import SQLALCHEMY_DATABASE_URL, Base

chat_metadata = MetaData()




class Message(Base):
    __tablename__ = "Message"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('User.id', ondelete='CASCADE'))
    text = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User", back_populates="messages")


engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


