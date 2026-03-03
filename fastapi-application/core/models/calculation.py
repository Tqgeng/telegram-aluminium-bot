from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    DateTime,
    Numeric,
    func,
)

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class Calculation(Base, IdIntPkMix):
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    construction_type = Column(String(64), nullable=False)
    profile_system = Column(String(128), nullable=True)
    width = Column(Numeric(8, 2), nullable=False)
    height = Column(Numeric(8, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    area = Column(Numeric(10, 3), nullable=False)

    material_cost = Column(Numeric(12, 2), nullable=False)
    labor_cost = Column(Numeric(12, 2), nullable=False)
    additional_cost = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
