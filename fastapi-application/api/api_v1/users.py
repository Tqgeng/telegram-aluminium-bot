from fastapi import APIRouter

from core.shemas.user import (
    UserRead,
    UserUpdate,
)
from .fastapi_users_router import fastapi_users
from core.config import settings

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

# /me /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
