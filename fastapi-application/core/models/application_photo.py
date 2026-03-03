from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
    func,
)

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class ApplicationPhoto(Base, IdIntPkMix):
    application_id = Column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    file_id = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    application = relationship("Application", back_populates="photos")
