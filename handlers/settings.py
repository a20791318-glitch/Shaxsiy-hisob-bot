from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database.db import set_user_currency, clear_user_data
from keyboards import (
    settings_menu_kb, currency_select_kb, clear_confirm_kb, clear_final_kb,
    main_menu_kb, back_main_kb
)

router = Router()

CURRENCY_MAP = {
    "currency_rub": ("RUB", "🇷🇺 RUB ₽"),
    "currency_usd": ("USD", "🇺🇸 USD $"),
    "currency_uzs": ("UZS", "🇺🇿 UZS so'm"),
    "currency_eur": ("EUR", "🇪🇺 EUR €"),
}


@router.callback_query(F.data == "settings_menu")
async def settings_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "⚙️ <b>Sozlamalar bo'limi</b> 👇",
        reply_markup=settings_menu_kb()
    )
    await call.answer()


@router.callback_query(F.data == "settings_currency")
async def settings_currency(call: CallbackQuery):
    await call.message.edit_text(
        "💱 <b>Yangi asosiy valyutani tanlang</b> 👇",
        reply_markup=currency_select_kb(back_cb="settings_menu")
    )
    await call.answer()


@router.callback_query(F.data.in_(CURRENCY_MAP.keys()))
async def currency_selected(call: CallbackQuery):
    code, label = CURRENCY_MAP[call.data]
    await set_user_currency(call.from_user.id, code)
    is_admin = call.from_user.id in ADMIN_IDS
    await call.message.edit_text(
        f"✅ <b>Asosiy valyuta yangilandi</b>\n\n💱 Yangi valyuta:\n{label}",
        reply_markup=main_menu_kb(is_admin=is_admin)
    )
    await call.answer()


@router.callback_query(F.data == "settings_clear")
async def settings_clear(call: CallbackQuery):
    await call.message.edit_text(
        "⚠️ <b>Barcha ma'lumotlar o'chiriladi:</b>\n\n"
        "- kirimlar\n- xarajatlar\n- qarzlar\n- hisobotlar\n- kategoriyalar\n\n"
        "Davom etasizmi?",
        reply_markup=clear_confirm_kb()
    )
    await call.answer()


@router.callback_query(F.data == "clear_confirm")
async def clear_confirm(call: CallbackQuery):
    await call.message.edit_text(
        "⚠️ <b>Oxirgi tasdiq</b>\n\nMa'lumotlarni tiklab bo'lmaydi.",
        reply_markup=clear_final_kb()
    )
    await call.answer()


@router.callback_query(F.data == "clear_all")
async def clear_all(call: CallbackQuery):
    await clear_user_data(call.from_user.id)
    await call.message.edit_text(
        "✅ <b>Barcha ma'lumotlar tozalandi</b>\n\n📭 Hisob yangi holatga qaytdi",
        reply_markup=main_menu_kb(is_admin=call.from_user.id in ADMIN_IDS)
    )
    await call.answer()
