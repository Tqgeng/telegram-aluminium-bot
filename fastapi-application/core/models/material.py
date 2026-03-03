from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    DateTime,
    Enum,
    Numeric,
    func,
)
import enum

from .base import Base
from .mixin.int_id_pk import IdIntPkMix


class MaterialCategory(str, enum.Enum):
    windows = "windows"
    doors = "doors"
    facades = "facades"
    partitions = "partitions"
    showcases = "showcases"
    others = "others"


class MaterialType(str, enum.Enum):
    profile = "profile"
    glazing = "glazing"
    fittings = "fittings"
    components = "components"


class Material(Base, IdIntPkMix):
    name = Column(String(255), nullable=False)
    category = Column(Enum(MaterialCategory, native_name=False), nullable=False)
    type = Column(Enum(MaterialType, native_name=False), nullable=False)
    price_per_unit = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(32), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    in_stock = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
