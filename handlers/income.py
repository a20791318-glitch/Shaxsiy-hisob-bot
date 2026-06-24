from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import IncomeState
from database.db import add_income, get_balance, get_recent_incomes
from keyboards import income_menu_kb, income_currency_kb, after_income_kb, back_main_kb
from config import CURRENCY_RATES

router = Router()


@router.callback_query(F.data == "income_menu")
async def income_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "💰 <b>Kirim turini tanlang</b> 👇",
        reply_markup=income_menu_kb()
    )
    await call.answer()


@router.callback_query(F.data == "income_cash")
async def income_cash(call: CallbackQuery, state: FSMContext):
    await state.set_state(IncomeState.cash_amount)
    await state.update_data(income_type="cash")
    await call.message.edit_text("💵 <b>Naqd summani kiriting:</b>")
    await call.answer()


@router.callback_query(F.data == "income_card")
async def income_card(call: CallbackQuery, state: FSMContext):
    await state.set_state(IncomeState.card_amount)
    await state.update_data(income_type="card")
    await call.message.edit_text("💳 <b>Karta summani kiriting:</b>")
    await call.answer()


@router.callback_query(F.data == "income_currency")
async def income_currency(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "💱 <b>Valyutani tanlang</b> 👇",
        reply_markup=income_currency_kb()
    )
    await call.answer()


@router.callback_query(F.data.in_({"income_usd", "income_eur", "income_uzs"}))
async def income_currency_selected(call: CallbackQuery, state: FSMContext):
    currency_map = {"income_usd": "USD", "income_eur": "EUR", "income_uzs": "UZS"}
    cur = currency_map[call.data]
    await state.set_state(IncomeState.currency_amount)
    await state.update_data(income_type="currency", currency=cur)
    symbols = {"USD": "$", "EUR": "€", "UZS": "so'm"}
    await call.message.edit_text(f"💵 <b>{cur} ({symbols[cur]}) summani kiriting:</b>")
    await call.answer()


@router.message(IncomeState.cash_amount)
@router.message(IncomeState.card_amount)
async def process_income_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting (raqam)")
        return
    amount = float(text)
    if amount < 1 or amount > 100_000_000:
        await message.answer("⚠️ Minimal: 1 — Maksimal: 100,000,000")
        return

    data = await state.get_data()
    inc_type = data.get("income_type", "cash")
    await add_income(message.from_user.id, inc_type, amount, amount, "RUB", 1.0)
    balance = await get_balance(message.from_user.id)

    icon = "💵" if inc_type == "cash" else "💳"
    label = "Naqd" if inc_type == "cash" else "Karta"
    from datetime import date
    await message.answer(
        f"✅ <b>Kirim qo'shildi</b>\n\n"
        f"{icon} {label}:\n<b>{amount:,.0f}₽</b>\n\n"
        f"📆 Sana:\n{date.today().strftime('%d.%m.%Y')}\n\n"
        f"💰 Balans:\n<b>{balance:,.0f}₽</b>",
        reply_markup=after_income_kb()
    )
    await state.clear()


@router.message(IncomeState.currency_amount)
async def process_currency_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting (raqam)")
        return
    amount_orig = float(text)
    data = await state.get_data()
    currency = data.get("currency", "USD")
    rate = CURRENCY_RATES.get(currency, 1.0)
    amount_rub = amount_orig * rate

    symbols = {"USD": "$", "EUR": "€", "UZS": "so'm"}
    sym = symbols.get(currency, "")

    await add_income(message.from_user.id, "currency", amount_rub, amount_orig, currency, rate)
    balance = await get_balance(message.from_user.id)

    from datetime import date
    await message.answer(
        f"✅ <b>Valyuta kirimi qo'shildi</b>\n\n"
        f"💵 {currency}:\n<b>{amount_orig:,.2f}{sym}</b>\n\n"
        f"📈 Kurs:\n<b>{rate}₽</b>\n\n"
        f"💰 RUB:\n<b>{amount_rub:,.0f}₽</b>\n\n"
        f"📆 Sana:\n{date.today().strftime('%d.%m.%Y')}\n\n"
        f"💵 Balans:\n<b>{balance:,.0f}₽</b>",
        reply_markup=after_income_kb()
    )
    await state.clear()


@router.callback_query(F.data == "income_history")
async def income_history(call: CallbackQuery, state: FSMContext):
    await state.clear()
    rows = await get_recent_incomes(call.from_user.id, limit=10)
    if not rows:
        await call.message.edit_text(
            "📋 <b>Kirimlar tarixi bo'sh</b>",
            reply_markup=back_main_kb("income_menu")
        )
        await call.answer()
        return

    type_icons = {"cash": "💵 Naqd", "card": "💳 Karta", "currency": "🪙 Valyuta"}
    text = "📋 <b>SO'NGGI KIRIMLAR</b>\n\n"
    for i, row in enumerate(rows, 1):
        label = type_icons.get(row["type"], row["type"])
        from datetime import datetime
        d = row["created_at"].strftime("%d.%m.%Y") if isinstance(row["created_at"], datetime) else str(row["created_at"])
        if row["currency"] not in ("RUB", None) and row["currency"]:
            sym = {"USD": "$", "EUR": "€", "UZS": "so'm"}.get(row["currency"], "")
            text += f"{i}️⃣ {label}\n{row['amount_original']:,.2f}{sym}\n({row['amount']:,.0f}₽)\n🕒 {d}\n\n"
        else:
            text += f"{i}️⃣ {label}\n{row['amount']:,.0f}₽\n🕒 {d}\n\n"

    await call.message.edit_text(text, reply_markup=back_main_kb("income_menu"))
    await call.answer()
