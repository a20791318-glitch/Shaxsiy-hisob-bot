from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import DebtTakeState, DebtGiveState, DebtPayState
from database.db import add_debt, get_active_debts, get_all_debts, get_debt_by_id, pay_debt
from keyboards import (
    debt_menu_kb, after_debt_kb, active_debts_kb, debt_pay_list_kb, back_main_kb
)

router = Router()


@router.callback_query(F.data == "debt_menu")
async def debt_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "🤝 <b>Qarz bo'limi</b> 👇",
        reply_markup=debt_menu_kb()
    )
    await call.answer()


# ---- QARZ OLISH ----

@router.callback_query(F.data == "debt_take")
async def debt_take(call: CallbackQuery, state: FSMContext):
    await state.set_state(DebtTakeState.person)
    await call.message.edit_text(
        "👤 <b>Kimdan qarz oldingiz?</b>\n\n📌 Namuna 👇\nAli\nAkmal\nOtabek"
    )
    await call.answer()


@router.message(DebtTakeState.person)
async def debt_take_person(message: Message, state: FSMContext):
    await state.update_data(person=message.text.strip())
    await state.set_state(DebtTakeState.amount)
    await message.answer("💰 <b>Summani kiriting:</b>")


@router.message(DebtTakeState.amount)
async def debt_take_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting")
        return
    amount = float(text)
    if amount < 1 or amount > 100_000_000:
        await message.answer("⚠️ Minimal: 1 — Maksimal: 100,000,000")
        return
    await state.update_data(amount=amount)
    await state.set_state(DebtTakeState.comment)
    await message.answer(
        "📝 <b>Izoh kiriting:</b>\n\n📌 Namuna 👇\nPatent uchun\nOvqat uchun\nUyga yuborish"
    )


@router.message(DebtTakeState.comment)
async def debt_take_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text.strip()
    await add_debt(message.from_user.id, "debt_taken", data["person"], data["amount"], comment)
    from datetime import date
    await message.answer(
        f"✅ <b>Qarz saqlandi</b>\n\n"
        f"📥 <b>Qarz olindi</b>\n\n"
        f"👤 {data['person']}\n\n"
        f"💰 Summa:\n<b>{data['amount']:,.0f}₽</b>\n\n"
        f"📝 Izoh:\n{comment}\n\n"
        f"📆 Sana:\n{date.today().strftime('%d.%m.%Y')}",
        reply_markup=after_debt_kb()
    )
    await state.clear()


# ---- QARZ BERISH ----

@router.callback_query(F.data == "debt_give")
async def debt_give(call: CallbackQuery, state: FSMContext):
    await state.set_state(DebtGiveState.person)
    await call.message.edit_text(
        "👤 <b>Kimga qarz berdingiz?</b>\n\n📌 Namuna 👇\nBekzod\nJavohir\nSherzod"
    )
    await call.answer()


@router.message(DebtGiveState.person)
async def debt_give_person(message: Message, state: FSMContext):
    await state.update_data(person=message.text.strip())
    await state.set_state(DebtGiveState.amount)
    await message.answer("💰 <b>Summani kiriting:</b>")


@router.message(DebtGiveState.amount)
async def debt_give_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting")
        return
    amount = float(text)
    if amount < 1 or amount > 100_000_000:
        await message.answer("⚠️ Minimal: 1 — Maksimal: 100,000,000")
        return
    await state.update_data(amount=amount)
    await state.set_state(DebtGiveState.comment)
    await message.answer(
        "📝 <b>Izoh kiriting:</b>\n\n📌 Namuna 👇\nOvqat uchun\nIsh haqqi\nUyiga yuboradi"
    )


@router.message(DebtGiveState.comment)
async def debt_give_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text.strip()
    await add_debt(message.from_user.id, "debt_given", data["person"], data["amount"], comment)
    from datetime import date
    await message.answer(
        f"✅ <b>Qarz saqlandi</b>\n\n"
        f"📤 <b>Qarz berildi</b>\n\n"
        f"👤 {data['person']}\n\n"
        f"💰 Summa:\n<b>{data['amount']:,.0f}₽</b>\n\n"
        f"📝 Izoh:\n{comment}\n\n"
        f"📆 Sana:\n{date.today().strftime('%d.%m.%Y')}",
        reply_markup=after_debt_kb()
    )
    await state.clear()


# ---- TO'LOV ----

@router.callback_query(F.data == "debt_pay_list")
async def debt_pay_list(call: CallbackQuery, state: FSMContext):
    await state.clear()
    debts = await get_active_debts(call.from_user.id)
    if not debts:
        await call.message.edit_text(
            "📋 Hozircha aktiv qarzlar yo'q",
            reply_markup=back_main_kb("debt_menu")
        )
        await call.answer()
        return
    await call.message.edit_text(
        "📋 <b>Qarzni tanlang</b> 👇",
        reply_markup=debt_pay_list_kb(debts)
    )
    await call.answer()


@router.callback_query(F.data.startswith("debt_pay_"))
async def debt_pay_selected(call: CallbackQuery, state: FSMContext):
    debt_id = int(call.data.split("_")[-1])
    debt = await get_debt_by_id(debt_id)
    if not debt:
        await call.answer("Qarz topilmadi", show_alert=True)
        return
    await state.set_state(DebtPayState.amount)
    await state.update_data(debt_id=debt_id, debt_type=debt["type"])
    label = "To'langan" if debt["type"] == "debt_taken" else "Qaytarilgan"
    await call.message.edit_text(
        f"👤 <b>{debt['person']}</b>\n"
        f"💰 Jami: {debt['amount']:,.0f}₽\n"
        f"📌 Qoldi: {debt['remaining']:,.0f}₽\n\n"
        f"💰 <b>{label} summani kiriting:</b>"
    )
    await call.answer()


@router.message(DebtPayState.amount)
async def process_debt_pay(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting")
        return
    amount = float(text)
    if amount < 1:
        await message.answer("⚠️ Minimal to'lov: 1")
        return

    data = await state.get_data()
    debt_id = data["debt_id"]
    debt = await get_debt_by_id(debt_id)
    remaining, status = await pay_debt(debt_id, amount, message.from_user.id)

    if status == "closed":
        from keyboards import back_main_kb
        await message.answer(
            f"✅ <b>Qarz yopildi</b>\n\n"
            f"👤 {debt['person']}\n\n"
            f"💰 {debt['amount']:,.0f}₽\n\n"
            f"🟢 Status:\nYopilgan",
            reply_markup=back_main_kb("debt_menu")
        )
    else:
        paid_label = "To'landi" if debt["type"] == "debt_taken" else "Qaytdi"
        from keyboards import after_debt_kb
        await message.answer(
            f"✅ <b>To'lov saqlandi</b>\n\n"
            f"👤 {debt['person']}\n\n"
            f"💰 Jami qarz:\n{debt['amount']:,.0f}₽\n\n"
            f"💸 {paid_label}:\n{amount:,.0f}₽\n\n"
            f"📌 Qoldi:\n{remaining:,.0f}₽",
            reply_markup=after_debt_kb()
        )
    await state.clear()


# ---- AKTIV QARZLAR ----

@router.callback_query(F.data == "debt_active")
async def debt_active(call: CallbackQuery, state: FSMContext):
    await state.clear()
    debts = await get_active_debts(call.from_user.id)
    if not debts:
        await call.message.edit_text(
            "📋 Hozircha aktiv qarzlar yo'q",
            reply_markup=back_main_kb("debt_menu")
        )
        await call.answer()
        return

    taken = [d for d in debts if d["type"] == "debt_taken"]
    given = [d for d in debts if d["type"] == "debt_given"]

    text = "📋 <b>AKTIV QARZLAR</b>\n\n"
    if taken:
        text += "📥 <b>Olingan qarzlar</b>\n"
        for d in taken:
            from datetime import datetime
            dt = d["created_at"].strftime("%d.%m.%Y") if isinstance(d["created_at"], datetime) else str(d["created_at"])
            text += f"\n👤 {d['person']}\n💰 {d['remaining']:,.0f}₽ qoldi\n📝 {d['comment']}\n📆 {dt}\n"

    if given:
        text += "\n📤 <b>Berilgan qarzlar</b>\n"
        for d in given:
            from datetime import datetime
            dt = d["created_at"].strftime("%d.%m.%Y") if isinstance(d["created_at"], datetime) else str(d["created_at"])
            text += f"\n👤 {d['person']}\n💰 {d['remaining']:,.0f}₽ qoldi\n📝 {d['comment']}\n📆 {dt}\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💸 To'lov qilish", callback_data="debt_pay_list"),
        ],
        [InlineKeyboardButton(text="📜 Qarz tarixi", callback_data="debt_history")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="debt_menu")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


# ---- QARZ TARIXI ----

@router.callback_query(F.data == "debt_history")
async def debt_history(call: CallbackQuery, state: FSMContext):
    await state.clear()
    debts = await get_all_debts(call.from_user.id)
    if not debts:
        await call.message.edit_text(
            "📜 Qarz tarixi bo'sh",
            reply_markup=back_main_kb("debt_menu")
        )
        await call.answer()
        return

    text = "📜 <b>QARZ TARIXI</b>\n\n"
    for i, d in enumerate(debts, 1):
        icon = "📥" if d["type"] == "debt_taken" else "📤"
        status_icon = "🟢 Yopilgan" if d["status"] == "closed" else "🟡 Aktiv"
        from datetime import datetime
        dt = d["created_at"].strftime("%d.%m.%Y") if isinstance(d["created_at"], datetime) else str(d["created_at"])
        text += f"{i}️⃣ {icon} {d['person']}\n💰 {d['amount']:,.0f}₽\n📝 {d['comment']}\n{status_icon}\n"
        if d["status"] == "active":
            text += f"📌 {d['remaining']:,.0f}₽ qoldi\n"
        text += f"📆 {dt}\n\n"

    await call.message.edit_text(text, reply_markup=back_main_kb("debt_menu"))
    await call.answer()
