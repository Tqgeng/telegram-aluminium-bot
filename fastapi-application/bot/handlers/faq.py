import json
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.faq_states import FAQStates
from bot.keyboards.main_menu import main_menu_kb

router = Router()

FAQ_PATH = Path(__file__).resolve().parent.parent / "utils" / "faq.json"


def load_faq():
    with FAQ_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


@router.message(F.text == "❓ Часто задаваемые вопросы")
async def faq_list(message: Message, state: FSMContext):
    items = load_faq()
    text = "FAQ:\n" + "\n".join([f"{i['q']}" for i in items])
    text += "\n\nНапишите ключевое слово для поиска."
    await state.set_state(FAQStates.waiting_query)
    await message.answer(text)


@router.message(FAQStates.waiting_query)
async def faq_search(message: Message, state: FSMContext):
    query = message.text.lower().strip()
    items = load_faq()
    results = [i for i in items if query in i["q"].lower() or query in i["a"].lower()]

    if not results:
        await message.answer(
            "Ничего не найдено. Для сложных запросов - 📞 Контакты.",
            reply_markup=main_menu_kb(),
        )
        return

    for item in results:
        text = f"❓ {item['q']}\n\n✅ {item['a']}"
        await message.answer(text)

    await state.clear()
