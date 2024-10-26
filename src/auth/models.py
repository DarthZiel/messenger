from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import relationship

from src.database import SQLALCHEMY_DATABASE_URL, Base

auth_metadata = MetaData()


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, index=True)
    password = Column(String(200), index=True)
    hashed_password = Column(String)
    messages = relationship('Message', back_populates="user")
    participant_one = relationship('Chat', foreign_keys='Chat.participant_one_id', back_populates='participant_one_id', cascade='all, delete-orphan')
    participant_two = relationship('Chat', foreign_keys='Chat.participant_two_id', back_populates='participant_two_id', cascade='all, delete-orphan')






engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
