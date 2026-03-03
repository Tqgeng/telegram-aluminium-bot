from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Text,
    DateTime,
    Enum,
    Numeric,
    func,
)
import enum

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class ApplicationStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"


class Application(Base, IdIntPkMix):
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    contact_name = Column(String(255), nullable=True)

    phone = Column(String(32), nullable=False)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    status = Column(
        Enum(ApplicationStatus, native_enum=False),
        nullable=False,
        default=ApplicationStatus.new,
    )
    estimated_cost = Column(Numeric(12, 2), nullable=True)
    crm_id = Column(String(128), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="applications")
    photos = relationship(
        "ApplicationPhoto", back_populates="application", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "ManagerNotification",
        back_populates="application",
        cascade="all, delete-orphan",
    )
