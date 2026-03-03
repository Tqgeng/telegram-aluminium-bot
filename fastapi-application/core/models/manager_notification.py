from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    BigInteger,
    DateTime,
    func,
)

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class ManagerNotification(Base, IdIntPkMix):
    manager_id = Column(BigInteger, nullable=False)
    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    notified_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    viewed_at = Column(DateTime(timezone=True), nullable=True)

    application = relationship("Application", back_populates="notifications")
