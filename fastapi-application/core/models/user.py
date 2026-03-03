from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, func

from core.types.user_id import UserIdType
from .base import Base
from .mixin.int_id_pk import IdIntPkMix

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(Base, IdIntPkMix, SQLAlchemyBaseUserTable[UserIdType]):
    email = Column(String(320), unique=True, index=True, nullable=True)
    hashed_password = Column(String(1024), nullable=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    phone = Column(String(32), nullable=True)
    name = Column(String(255), nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    applications = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
