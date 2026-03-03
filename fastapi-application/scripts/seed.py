import asyncio
import os
import sys

from sqlalchemy import select

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from core.models import db_helper, User, Material, PriceCoefficient
from core.models.material import MaterialCategory, MaterialType
from core.models.price_coefficient import CoefficientType
from core.authentication.user_manager import UserManager
from core.shemas.user import UserCreate

MATERIALS: list[dict] = [
    # profile
    {
        "name": "45mm",
        "category": MaterialCategory.windows,
        "type": MaterialType.profile,
        "price_per_unit": 2500,
        "unit": "м²",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
    # glazing
    {
        "name": "Стеклопакет",
        "category": MaterialCategory.windows,
        "type": MaterialType.glazing,
        "price_per_unit": 2200,
        "unit": "м²",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
    # fittings
    {
        "name": "Фурнитура: стандарт",
        "category": MaterialCategory.windows,
        "type": MaterialType.fittings,
        "price_per_unit": 800,
        "unit": "шт",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
    # package materials
    {
        "name": "Москитная сетка: да",
        "category": MaterialCategory.windows,
        "type": MaterialType.components,
        "price_per_unit": 500,
        "unit": "шт",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
    {
        "name": "Уплотнители: стандартные",
        "category": MaterialCategory.windows,
        "type": MaterialType.components,
        "price_per_unit": 200,
        "unit": "шт",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
    {
        "name": "Подоконник: нет",
        "category": MaterialCategory.windows,
        "type": MaterialType.components,
        "price_per_unit": 0,
        "unit": "шт",
        "description": "",
        "image_url": None,
        "in_stock": True,
    },
]

COEFFICIENTS: list[dict] = [
    {"name": "Базовая сложность", "type": CoefficientType.complexity, "value": 1.0},
    {"name": "Сложный монтаж", "type": CoefficientType.complexity, "value": 1.3},
    {"name": "Сезонная скидка", "type": CoefficientType.seasonal, "value": 0.95},
    {"name": "Монтаж", "type": CoefficientType.region, "value": 0.05},
    {"name": "Демонтаж", "type": CoefficientType.region, "value": 0.03},
    {"name": "Отделка откосов", "type": CoefficientType.region, "value": 0.02},
    {"name": "Герметизация", "type": CoefficientType.region, "value": 0.01},
    {"name": "Доставка", "type": CoefficientType.region, "value": 0.03},
]


async def seed_materials(session):
    for item in MATERIALS:
        stmt = select(Material).where(
            Material.name == item["name"],
            Material.category == item["category"],
            Material.type == item["type"],
        )
        existing = await session.scalar(stmt)
        if existing:
            existing.price_per_unit = item["price_per_unit"]
            existing.unit = item["unit"]
            existing.description = item["description"]
            existing.image_url = item["image_url"]
            existing.in_stock = item["in_stock"]
        else:
            session.add(Material(**item))


async def seed_coefficients(session):
    for item in COEFFICIENTS:
        stmt = select(PriceCoefficient).where(
            PriceCoefficient.name == item["name"],
            PriceCoefficient.type == item["type"],
        )
        existing = await session.scalar(stmt)
        if existing:
            existing.value = item["value"]
        else:
            session.add(PriceCoefficient(**item))


async def seed_admin(session):
    email = os.getenv("SEED_ADMIN_EMAIL")
    password = os.getenv("SEED_ADMIN_PASSWORD")
    if not email or not password:
        return

    stmt = select(User).where(User.email == email)
    existing = await session.scalar(stmt)
    if existing:
        return

    user_db = User.get_db(session=session)
    user_manager = UserManager(user_db)

    user_create = UserCreate(
        email=email,
        password=password,
        is_superuser=True,
        is_verified=True,
    )

    user = await user_manager.create(user_create, safe=False, request=None)


async def main():
    async with db_helper.session_factory() as session:
        await seed_materials(session)
        await seed_coefficients(session)
        await seed_admin(session)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
