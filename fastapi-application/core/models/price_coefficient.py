from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    Numeric,
    func,
)
import enum

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class CoefficientType(str, enum.Enum):
    complexity = "complexity"
    region = "region"
    discount = "discount"
    seasonal = "seasonal"
    promo = "promo"


class PriceCoefficient(Base, IdIntPkMix):
    name = Column(String(255), nullable=False)
    type = Column(Enum(CoefficientType, native_enum=False), nullable=False)
    value = Column(Numeric(8, 3), nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
