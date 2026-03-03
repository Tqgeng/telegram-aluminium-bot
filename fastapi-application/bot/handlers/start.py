from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards.main_menu import main_menu_kb

router = Router()

WELCOME_TEXT = (
    "Добро пожаловать! 👋 \n\n"
    "Мы специализируемся на продаже и установке алюминиевых конструкций: \n"
    "✅ Окна и двери\n"
    "✅ Фасады и витрины\n"
    "✅ Перегородки и системы\n\n"
    "Что вас интересует?"
)


@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


@router.message(F.text == "📞 Наши контакты")
async def contacts(message: Message):
    await message.answer("Контакты: +7 (999) 123-45-67")
