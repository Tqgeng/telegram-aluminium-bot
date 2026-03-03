from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User
from core.shemas.user import UserCreate


async def get_all_users(session: AsyncSession) -> Sequence[User]:
    stmt = select(User).order_by(User.id)
    result = await session.scalars(stmt)
    return result.all()

async def search_user(
    session: AsyncSession,
    q: str,
) -> Sequence[User]:
    query = select(User)
    if not q:
        return []
    if q:
        query = query.where(User.username.ilike(f"%{q}%"))
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def create_user(
    user_create: UserCreate,
    session: AsyncSession,
) -> User:
    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
