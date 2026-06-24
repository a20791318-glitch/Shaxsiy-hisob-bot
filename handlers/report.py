from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.db import get_balance, get_weekly_report, get_monthly_report
from keyboards import report_menu_kb, back_main_kb

router = Router()


@router.callback_query(F.data == "report_menu")
async def report_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "📊 <b>Hisobot bo'limi</b> 👇",
        reply_markup=report_menu_kb()
    )
    await call.answer()


@router.callback_query(F.data == "report_weekly")
async def report_weekly(call: CallbackQuery):
    income, expense, cats = await get_weekly_report(call.from_user.id)
    balance = await get_balance(call.from_user.id)
    profit = income - expense

    text = (
        "📅 <b>HAFTALIK HISOBOT</b>\n"
        "━━━━━━━━━━\n\n"
        f"💰 Kirim: <b>{income:,.0f}₽</b>\n"
        f"➖ Xarajat: <b>{expense:,.0f}₽</b>\n"
        f"📈 Foyda: <b>{profit:,.0f}₽</b>\n"
        f"💵 Balans: <b>{balance:,.0f}₽</b>\n\n"
    )
    if cats:
        text += "📂 <b>Xarajat kategoriyalari:</b>\n"
        for row in cats:
            text += f"• {row['category_name']}: {row['total']:,.0f}₽\n"

    await call.message.edit_text(text, reply_markup=back_main_kb("report_menu"))
    await call.answer()


@router.callback_query(F.data == "report_monthly")
async def report_monthly(call: CallbackQuery):
    income, expense, cats = await get_monthly_report(call.from_user.id)
    balance = await get_balance(call.from_user.id)
    profit = income - expense

    text = (
        "📆 <b>OYLIK HISOBOT</b>\n"
        "━━━━━━━━━━\n\n"
        f"💰 Kirim: <b>{income:,.0f}₽</b>\n"
        f"➖ Xarajat: <b>{expense:,.0f}₽</b>\n"
        f"📈 Foyda: <b>{profit:,.0f}₽</b>\n"
        f"💵 Balans: <b>{balance:,.0f}₽</b>\n\n"
    )
    if cats:
        text += "📂 <b>Xarajat kategoriyalari:</b>\n"
        for row in cats:
            text += f"• {row['category_name']}: {row['total']:,.0f}₽\n"

    await call.message.edit_text(text, reply_markup=back_main_kb("report_menu"))
    await call.answer()
