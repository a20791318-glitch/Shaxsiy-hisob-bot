from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import ExpenseState
from database.db import get_categories, add_category, add_expense, get_balance, get_recent_expenses
from keyboards import expense_menu_kb, expense_no_cat_kb, after_expense_kb, back_main_kb

router = Router()


@router.callback_query(F.data == "expense_menu")
async def expense_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    categories = await get_categories(call.from_user.id)
    if not categories:
        await call.message.edit_text(
            "📂 Sizda hali xarajat kategoriyalari mavjud emas.\n\nYangi kategoriya qo'shing 👇",
            reply_markup=expense_no_cat_kb()
        )
    else:
        await call.message.edit_text(
            "📂 <b>Xarajat kategoriyasini tanlang</b> 👇",
            reply_markup=expense_menu_kb(categories)
        )
    await call.answer()


@router.callback_query(F.data == "expense_add_category")
async def expense_add_category(call: CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseState.add_category)
    await call.message.edit_text(
        "📝 <b>Yangi kategoriya nomini kiriting</b>\n\n"
        "📌 Namuna 👇\n🍔 Ovqat\n🚕 Taxi\n💊 Dori"
    )
    await call.answer()


@router.message(ExpenseState.add_category)
async def process_add_category(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 1 or len(name) > 50:
        await message.answer("⚠️ Kategoriya nomi 1-50 belgi bo'lishi kerak")
        return
    await add_category(message.from_user.id, name)
    categories = await get_categories(message.from_user.id)
    await message.answer(
        f"✅ <b>Kategoriya yaratildi</b>\n\n📂 {name}\n\nEndi ushbu kategoriya orqali xarajat qo'shishingiz mumkin 👇",
        reply_markup=expense_menu_kb(categories)
    )
    await state.clear()


@router.callback_query(F.data.startswith("expense_cat_"))
async def expense_cat_selected(call: CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split("_")[-1])
    categories = await get_categories(call.from_user.id)
    cat = next((c for c in categories if c["id"] == cat_id), None)
    if not cat:
        await call.answer("Kategoriya topilmadi", show_alert=True)
        return
    await state.set_state(ExpenseState.expense_amount)
    await state.update_data(cat_id=cat_id, cat_name=cat["name"])
    await call.message.edit_text(f"{cat['name']} <b>uchun summani kiriting:</b>")
    await call.answer()


@router.message(ExpenseState.expense_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", ".")
    if not text.replace(".", "").isdigit():
        await message.answer("⚠️ Iltimos faqat summa kiriting (raqam)")
        return
    amount = float(text)
    if amount < 1 or amount > 100_000_000:
        await message.answer("⚠️ Minimal: 1 — Maksimal: 100,000,000")
        return

    data = await state.get_data()
    cat_id = data["cat_id"]
    cat_name = data["cat_name"]

    await add_expense(message.from_user.id, cat_id, cat_name, amount)
    balance = await get_balance(message.from_user.id)

    from datetime import date
    await message.answer(
        f"✅ <b>Xarajat qo'shildi</b>\n\n"
        f"📂 Kategoriya:\n{cat_name}\n\n"
        f"💰 Summa:\n<b>{amount:,.0f}₽</b>\n\n"
        f"📆 Sana:\n{date.today().strftime('%d.%m.%Y')}\n\n"
        f"💵 Balans:\n<b>{balance:,.0f}₽</b>",
        reply_markup=after_expense_kb()
    )
    await state.clear()


@router.callback_query(F.data == "expense_history")
async def expense_history(call: CallbackQuery, state: FSMContext):
    await state.clear()
    rows = await get_recent_expenses(call.from_user.id, limit=10)
    if not rows:
        await call.message.edit_text(
            "📋 <b>Xarajatlar tarixi bo'sh</b>",
            reply_markup=back_main_kb("expense_menu")
        )
        await call.answer()
        return

    text = "📋 <b>SO'NGGI XARAJATLAR</b>\n\n"
    for i, row in enumerate(rows, 1):
        from datetime import datetime
        d = row["created_at"].strftime("%d.%m.%Y") if isinstance(row["created_at"], datetime) else str(row["created_at"])
        text += f"{i}️⃣ {row['category_name']}\n{row['amount']:,.0f}₽\n🕒 {d}\n\n"

    await call.message.edit_text(text, reply_markup=back_main_kb("expense_menu"))
    await call.answer()
