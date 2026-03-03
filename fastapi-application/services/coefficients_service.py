from sqlalchemy import select

from core.models import db_helper, PriceCoefficient
from core.models.price_coefficient import CoefficientType


async def list_coefficient():
    async with db_helper.session_factory() as session:
        stmt = select(PriceCoefficient).order_by(PriceCoefficient.id)
        return (await session.scalars(stmt)).all()


async def add_coefficient(name, type_, value):
    async with db_helper.session_factory() as session:
        coefficient = PriceCoefficient(
            name=name,
            type=CoefficientType(type_),
            value=value,
        )
        session.add(coefficient)
        await session.commit()


async def update_coefficient(coefficient_id: int, value):
    async with db_helper.session_factory() as session:
        coefficient = await session.get(PriceCoefficient, coefficient_id)
        if not coefficient:
            raise ValueError("Коэффициент не найден")
        coefficient.value = value
        await session.commit()


async def delete_coefficient(coefficient_id):
    async with db_helper.session_factory() as session:
        coefficient = await session.get(PriceCoefficient, coefficient_id)
        if not coefficient:
            raise ValueError("Коэффициент не найден")
        session.delete(coefficient)
        await session.commit()
