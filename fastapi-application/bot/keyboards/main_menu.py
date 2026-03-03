from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Рассчитать стоимость"),
                KeyboardButton(text="📦 Каталог продуктов"),
            ],
            [
                KeyboardButton(text="📞 Наши контакты"),
                KeyboardButton(text="❓ Часто задаваемые вопросы"),
            ],
            [
                KeyboardButton(text="📝 Мои заявки"),
            ],
        ],
        resize_keyboard=True,
    )
