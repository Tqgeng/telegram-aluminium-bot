from aiogram import BaseMiddleware
from typing import Any, Dict

from bot.services.user_service import get_or_create_user


class UserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Any, data: Dict[str, Any]):
        tg_user = getattr(event, "from_user", None)
        if tg_user:
            user = await get_or_create_user(
                telegram_id=tg_user.id,
                name=tg_user.full_name,
            )
            data["db_user"] = user
        return await handler(event, data)
