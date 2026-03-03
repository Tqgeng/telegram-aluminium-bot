import logging
from aiogram import BaseMiddleware
from typing import Any, Dict, Callable, Awaitable
from core.config import settings

logger = logging.getLogger("errors")


class ErrorAlertMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.exception("Unhandled error: %s", e)
            bot = data.get("bot")
            if bot:
                await bot.send_message(
                    settings.telegram.manager_group_id,
                    f"🚨 Ошибка в боте:\n{e}",
                )
                raise
