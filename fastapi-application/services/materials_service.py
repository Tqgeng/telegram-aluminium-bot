from core.models import db_helper, Material
from core.models.material import MaterialCategory, MaterialType


async def add_material(name, category, type_, price, unit, description, in_stock: bool):
    async with db_helper.session_factory() as session:
        material = Material(
            name=name,
            category=MaterialCategory(category),
            type=MaterialType(type_),
            price_per_unit=price,
            unit=unit,
            description=description,
            in_stock=in_stock,
        )
        session.add(material)
        await session.commit()


async def update_material(material_id: int, price):
    async with db_helper.session_factory() as session:
        material = await session.get(Material, material_id)
        if not material:
            raise ValueError("Материал не найден")
        material.price_per_unit = price
        await session.commit()


async def delete_material(material_id: int):
    async with db_helper.session_factory() as session:
        material = await session.get(Material, material_id)
        if not material:
            raise ValueError("Материал не найден")
        await session.delete(material)
        await session.commit()
