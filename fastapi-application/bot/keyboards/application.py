from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def nav_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def photos_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Готово"), KeyboardButton(text="◀️ Назад")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def confirm_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Отправить заявку")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def apps_list_kb(
    app_ids: list[int],
    next_offset: int | None = None,
) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, app_id in enumerate(app_ids, 1):
        row.append(
            InlineKeyboardButton(
                text=f"Подробнее #{app_id}", callback_data=f"app_detail:{app_id}"
            )
        )
        if i % 2 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    if next_offset is not None:
        rows.append(
            [
                InlineKeyboardButton(
                    text="Показать еще", callback_data=f"app_more:{next_offset}"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)
