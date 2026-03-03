from sqlalchemy import select, update
from core.models import User, db_helper
from bot.utils.validators import normalize_phone


async def is_user_blocked(telegram_id: int) -> bool:
    async with db_helper.session_factory() as session:
        stmt = select(User.is_blocked).where(User.telegram_id == telegram_id)
        result = await session.scalar(stmt)
        return bool(result)


async def get_or_create_user(
    telegram_id: int,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> User:
    async with db_helper.session_factory() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = await session.scalar(stmt)
        if user:
            changed = False
            if name and user.name != name:
                user.name = name
                changed = True
            if phone and user.phone != phone:
                user.phone = phone
                changed = True
            if email and user.email != email:
                user.email = email
                changed = True
            if changed:
                await session.commit()
            return user

        user = User(
            telegram_id=telegram_id,
            name=name,
            phone=phone,
            email=email,
            is_active=True,
            is_verified=False,
            is_superuser=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def update_user_phone(telegram_id: int, phone_raw: str) -> None:
    phone = normalize_phone(phone_raw)
    if not phone:
        return
    async with db_helper.session_factory() as session:
        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(phone=phone)
        )
        await session.commit()


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    async with db_helper.session_factory() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        return await session.scalar(stmt)


async def get_user_by_id(user_id: int) -> User | None:
    async with db_helper.session_factory() as session:
        stmt = select(User).where(User.id == user_id)
        return await session.scalar(stmt)
