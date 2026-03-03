from sqlalchemy import select
from core.models import db_helper, Material


async def get_catalog(
    category=None,
    type_=None,
    in_stock=None,
    price_minimum=None,
    price_maximum=None,
    search=None,
):
    async with db_helper.session_factory() as session:
        stmt = select(Material)
        if category:
            stmt = stmt.where(Material.category == category)
        if type_:
            stmt = stmt.where(Material.type == type_)
        if in_stock is True:
            stmt = stmt.where(Material.in_stock.is_(True))
        if price_minimum is not None:
            stmt = stmt.where(Material.price_per_unit >= price_minimum)
        if price_maximum is not None:
            stmt = stmt.where(Material.price_per_unit <= price_maximum)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(
                Material.name.ilike(like) | Material.description.ilike(like)
            )

        result = await session.scalars(stmt)
        return list(result)
