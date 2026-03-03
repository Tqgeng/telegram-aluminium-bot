import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from datetime import datetime, timedelta

from bot.middlewares.logging import LoggingMiddleware
from bot.middlewares.antispam import AntiSpamMiddleware
from bot.middlewares.block_user import BlockUserMiddleware
from bot.middlewares.create_user import UserMiddleware
from bot.middlewares.error_alert import ErrorAlertMiddleware

from bot.utils.redis import get_redis
from bot.routers import setup_routes
from core.config import settings
from utils.logging import setup_logging

from bot.services.notification_service import notify_user
from services.application_service import (
    sync_crm_statuses,
    count_today_applications,
    get_stale_applications,
)

logger = logging.getLogger("bot")


def setup_despatcher(redis_url: str, redis_client) -> Dispatcher:
    storage = RedisStorage.from_url(url=redis_url)
    dp = Dispatcher(storage=storage)

    for observer in (dp.message, dp.callback_query):
        observer.middleware(UserMiddleware())
        observer.middleware(BlockUserMiddleware())
        observer.middleware(AntiSpamMiddleware(redis=redis_client, min_interval=1.0))
        observer.middleware(LoggingMiddleware())
        observer.middleware(ErrorAlertMiddleware())

    dp.include_router(setup_routes())
    return dp


async def status_watcher(bot):
    while True:
        try:
            await sync_crm_statuses(
                lambda tg_id, app_id, status: notify_user(bot, tg_id, app_id, status)
            )
        except Exception as e:
            logger.exception("status watcher failed", exc_info=e)
        await asyncio.sleep(60)


async def daily_report(bot):
    while True:
        count = await count_today_applications()
        await bot.send_message(
            settings.telegram.manager_group_id, f"За сегодня заявок: {count}"
        )
        now = datetime.now()
        next_run = (now + timedelta(days=1)).replace(
            hour=1, minute=0, second=0, microsecond=0
        )
        await asyncio.sleep((next_run - now).total_seconds())


async def stale_reminder(bot):
    while True:
        apps = await get_stale_applications(hours=1)
        if apps:
            await bot.send_message(
                settings.telegram.manager_group_id,
                f"Необработанные заявки: {len(apps)}",
            )
        await asyncio.sleep(900)


async def heartbeat():
    while True:
        logger.info("bot alive")
        await asyncio.sleep(300)


async def main():
    if not settings.telegram.bot_token:
        raise ValueError("FASTAPI__TELEGRAM__BOT_TOKEN not found in .env")

    setup_logging()
    bot = Bot(token=settings.telegram.bot_token)
    redis_url = (
        f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db.cache}"
    )
    redis_client = get_redis()
    dp = setup_despatcher(redis_url, redis_client)

    # task = asyncio.create_task(status_watcher(bot))
    task_report = asyncio.create_task(daily_report(bot))
    task_stale = asyncio.create_task(stale_reminder(bot))
    task_heartbeat = asyncio.create_task(heartbeat())

    try:
        await redis_client.ping()
        logger.info("Bot started polling")
        await dp.start_polling(bot)
    except Exception as e:
        await bot.send_message(
            settings.telegram.manager_group_id, f"🚨 Ошибка бота: {e}"
        )
        raise
    finally:
        # task.cancel()
        task_report.cancel()
        task_stale.cancel()
        task_heartbeat.cancel()
        logger.info("Shutting down...")
        await bot.session.close()
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
