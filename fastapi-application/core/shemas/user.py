import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr

from core.types.user_id import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    email: Optional[EmailStr] = None


class UserCreate(schemas.BaseUserCreate):
    email: Optional[EmailStr] = None


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
