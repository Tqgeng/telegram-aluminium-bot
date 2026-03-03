import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Any, Dict, Callable, Awaitable

logger = logging.getLogger("bot")


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            logger.info(
                "msg from=%s, text=%r",
                event.from_user.id if event.from_user else None,
                event.text,
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                "cb from=%s, data=%r",
                event.from_user.id if event.from_user else None,
                event.data,
            )
        return await handler(event, data)
