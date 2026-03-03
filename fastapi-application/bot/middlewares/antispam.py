from aiogram import BaseMiddleware
import logging

logger = logging.getLogger(__name__)


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, redis, min_interval: float = 1.0):
        self.redis = redis
        self.min_interval = min_interval

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)
        key = f"antispam:{user.id}"
        ok = await self.redis.set(key, "1", ex=max(1, int(self.min_interval)), nx=True)
        if not ok:
            logger.info("antispam blocked user=%s", user.id)
            return
        return await handler(event, data)
