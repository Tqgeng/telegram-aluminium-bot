from aiogram.types import Message
from core.config import settings


async def is_group_admin(message: Message) -> bool:
    if not message.chat or message.chat.id != settings.telegram.manager_group_id:
        return False
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")
