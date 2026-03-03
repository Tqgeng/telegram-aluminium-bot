from sqlalchemy import select, func
from core.models import db_helper, Application, PriceCoefficient


async def get_stats():
    async with db_helper.session_factory() as session:
        total = await session.scalar(select(func.count()).select_from(Application))
        avg_check = await session.scalar(select(func.avg(Application.estimated_cost)))
        return total or 0, avg_check or 0
