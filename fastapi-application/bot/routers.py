from aiogram import Router
from bot.handlers import (
    start,
    calculator,
    applications,
    catalog,
    faq,
    admin,
)


def setup_routes() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(calculator.router)
    router.include_router(applications.router)
    router.include_router(catalog.router)
    router.include_router(faq.router)
    router.include_router(admin.router)
    return router
