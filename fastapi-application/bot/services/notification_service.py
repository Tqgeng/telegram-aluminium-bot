from aiogram import Bot
from core.config import settings
from bot.keyboards.manager import manager_kb
from core.models import db_helper, ManagerNotification
from datetime import datetime, timezone
from sqlalchemy import update

status_map = {
    "new": "Новая",
    "in_progress": "В работе",
    "completed": "Завершена",
    "rejected": "Отклонена",
}


async def notify_manager(bot: Bot, app_id: int, text: str, phone: str):
    await bot.send_message(
        chat_id=settings.telegram.manager_group_id,
        text=text,
        reply_markup=manager_kb(app_id=app_id),
    )
    await log_manager_notification(app_id)


async def notify_user(bot, tg_id: int, app_id: int, status: str):
    status_txt = status_map.get(status, status)
    await bot.send_message(tg_id, f"Статус заявки #{app_id} изменился: {status_txt}")


async def log_manager_notification(application_id: int):
    async with db_helper.session_factory() as session:
        session.add(
            ManagerNotification(
                manager_id=int(settings.telegram.manager_group_id),
                application_id=application_id,
            )
        )
        await session.commit()


async def mark_manager_viewed(application_id: int):
    async with db_helper.session_factory() as session:
        await session.execute(
            update(ManagerNotification)
            .where(
                ManagerNotification.application_id == application_id,
                ManagerNotification.manager_id
                == int(settings.telegram.manager_group_id),
                ManagerNotification.viewed_at.is_(None),
            )
            .values(viewed_at=datetime.now(timezone.utc))
        )
        await session.commit()
