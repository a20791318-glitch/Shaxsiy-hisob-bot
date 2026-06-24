from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest

from config import CHANNEL_USERNAME, ADMIN_IDS
from database.db import get_or_create_user, get_user
from keyboards import main_menu_kb, subscribe_kb, currency_select_kb

router = Router()


async def check_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ("left", "kicked", "banned")
    except Exception:
        return False


def welcome_text(first_name: str, last_name: str = None) -> str:
    name = f"{first_name} {last_name}" if last_name else first_name
    return (
        f"Assalamu alaykum <b>{name}</b> 👋\n\n"
        "📊 <b>Shaxsiy Hisob Botiga xush kelibsiz.</b>\n\n"
        "Bu bot orqali:\n\n"
        "💰 Kirimlarni yozish\n"
        "➖ Xarajatlarni hisoblash\n"
        "🏡 Pul o'tkazmalarni saqlash\n"
        "🤝 Qarzlarni boshqarish\n"
        "📆 Haftalik/Oylik hisobotlarni ko'rish\n\n"
        "mumkin."
    )


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    await get_or_create_user(user.id, user.first_name, user.last_name, user.username)

    is_subscribed = await check_subscription(bot, user.id)
    if not is_subscribed:
        await message.answer(
            "⚠️ Botdan foydalanish uchun quyidagi kanalga obuna bo'ling 👇",
            reply_markup=subscribe_kb()
        )
        return

    db_user = await get_user(user.id)
    is_admin = user.id in ADMIN_IDS

    if not db_user["main_currency"]:
        await message.answer(
            "💱 <b>Asosiy valyutangizni tanlang</b> 👇\n\n"
            "📌 Bu:\n- hisobotlar\n- balans\n- hisob-kitoblar\nuchun ishlatiladi.",
            reply_markup=currency_select_kb(back_cb="main_menu")
        )
    else:
        await message.answer(
            welcome_text(user.first_name, user.last_name),
            reply_markup=main_menu_kb(is_admin=is_admin)
        )


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery, bot: Bot):
    is_subscribed = await check_subscription(bot, call.from_user.id)
    if not is_subscribed:
        await call.answer("❌ Siz hali kanalga obuna bo'lmadingiz", show_alert=True)
        return

    user = call.from_user
    db_user = await get_user(user.id)
    is_admin = user.id in ADMIN_IDS

    if not db_user or not db_user["main_currency"]:
        await call.message.edit_text(
            "💱 <b>Asosiy valyutangizni tanlang</b> 👇\n\n"
            "📌 Bu:\n- hisobotlar\n- balans\n- hisob-kitoblar\nuchun ishlatiladi.",
            reply_markup=currency_select_kb(back_cb="main_menu")
        )
    else:
        await call.message.edit_text(
            welcome_text(user.first_name, user.last_name),
            reply_markup=main_menu_kb(is_admin=is_admin)
        )
    await call.answer()


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(call: CallbackQuery):
    user = call.from_user
    is_admin = user.id in ADMIN_IDS
    try:
        await call.message.edit_text(
            welcome_text(user.first_name, user.last_name),
            reply_markup=main_menu_kb(is_admin=is_admin)
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@router.callback_query(F.data == "share")
async def share_callback(call: CallbackQuery):
    bot_info = await call.bot.get_me()
    text = (
        f"📊 <b>Shaxsiy Hisob Boti</b>\n\n"
        f"Bu bot orqali kirim, xarajat, qarz va hisobotlarni osonlikcha yuritish mumkin.\n\n"
        f"👉 @{bot_info.username}"
    )
    from keyboards import back_main_kb
    await call.message.edit_text(text, reply_markup=back_main_kb())
    await call.answer()
