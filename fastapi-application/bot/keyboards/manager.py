from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def manager_kb(app_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять", callback_data=f"app_accept:{app_id}"
                ),
                InlineKeyboardButton(
                    text="📞 Позвонить", callback_data=f"app_call:{app_id}"
                ),
                InlineKeyboardButton(text="📧 SMS", callback_data=f"app_sms:{app_id}"),
            ]
        ]
    )
