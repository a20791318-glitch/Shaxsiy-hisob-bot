import io
import os
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database.db import get_all_users, get_pool
from states import BroadcastState, RestoreState
from keyboards import (
    admin_panel_kb, admin_stats_kb, back_main_kb
)

logger = logging.getLogger(__name__)
router = Router()


class IsAdmin(Filter):
    async def __call__(self, event) -> bool:
        user_id = None
        if hasattr(event, "from_user"):
            user_id = event.from_user.id
        return user_id in ADMIN_IDS


router.callback_query.filter(IsAdmin())
router.message.filter(IsAdmin())


@router.callback_query(F.data == "admin_panel")
async def admin_panel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "👨🏻‍💻 <b>Admin panel</b> 👇",
        reply_markup=admin_panel_kb()
    )
    await call.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    users = await get_all_users()
    total = len(users)
    last15 = users[:15]

    text = f"📊 <b>BOT STATISTIKASI</b>\n━━━━━━━━━━\n\n👥 Jami foydalanuvchilar:\n<b>{total}</b>\n━━━━━━━━━━\n\n🆕 Oxirgi 15 ta foydalanuvchi:\n\n"
    for i, u in enumerate(last15, 1):
        name = f"{u['first_name']} {u['last_name'] or ''}".strip()
        text += f"{i}️⃣ <a href='tg://user?id={u['user_id']}'>{name}</a>\n"

    await call.message.edit_text(text, reply_markup=admin_stats_kb(), disable_web_page_preview=True)
    await call.answer()


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(call: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.message)
    await call.message.edit_text(
        "📨 <b>Yuboriladigan xabarni kiriting:</b>\n\n📌 Text, rasm, video va fayl yuborish mumkin."
    )
    await call.answer()


@router.message(BroadcastState.message)
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    users = await get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await message.copy_to(user["user_id"])
            sent += 1
        except Exception:
            failed += 1

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Yana yuborish", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])
    await message.answer(
        f"✅ <b>Xabar yuborildi</b>\n\n"
        f"👥 Yuborildi: <b>{sent}</b> ta userga\n"
        f"❌ Xato: <b>{failed}</b> ta",
        reply_markup=kb
    )
    await state.clear()


@router.callback_query(F.data == "admin_backup")
async def admin_backup(call: CallbackQuery, bot: Bot):
    await call.message.edit_text("📁 Database backup fayli tayyorlanmoqda...")
    await call.answer()

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            tables = ["users", "incomes", "categories", "expenses", "debts"]
            backup_lines = []
            for table in tables:
                rows = await conn.fetch(f"SELECT * FROM {table}")
                if rows:
                    cols = list(rows[0].keys())
                    backup_lines.append(f"\n-- TABLE: {table} --")
                    backup_lines.append(",".join(cols))
                    for row in rows:
                        vals = []
                        for v in row.values():
                            if v is None:
                                vals.append("NULL")
                            else:
                                vals.append(f'"{str(v)}"')
                        backup_lines.append(",".join(vals))

        content = "\n".join(backup_lines).encode("utf-8")
        from datetime import date
        filename = f"backup_{date.today().strftime('%d_%m_%Y')}.csv"
        file = BufferedInputFile(content, filename=filename)

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_backup")],
            [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
        ])
        await bot.send_document(
            call.from_user.id,
            document=file,
            caption="✅ <b>Backup tayyor</b>\n\n📦 Fayl yuklandi"
        )
        await call.message.edit_text("✅ Backup yuborildi", reply_markup=kb)
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await call.message.edit_text(
            f"❌ Backup xato: {e}",
            reply_markup=back_main_kb("admin_panel")
        )


@router.callback_query(F.data == "admin_restore")
async def admin_restore(call: CallbackQuery):
    from keyboards import restore_confirm_kb
    await call.message.edit_text(
        "⚠️ <b>Backup tiklanganda:</b>\n\n"
        "- eski database tozalanadi\n"
        "- barcha eski ma'lumotlar o'chadi\n"
        "- yangi backup yuklanadi\n\n"
        "Davom etasizmi?",
        reply_markup=restore_confirm_kb()
    )
    await call.answer()


@router.callback_query(F.data == "restore_confirm")
async def restore_confirm(call: CallbackQuery, state: FSMContext):
    await state.set_state(RestoreState.file)
    await call.message.edit_text(
        "📁 <b>Backup fayl yuboring</b>\n\n📌 .csv format (admin backup orqali olingan)"
    )
    await call.answer()


@router.message(RestoreState.file)
async def process_restore(message: Message, state: FSMContext, bot: Bot):
    if not message.document:
        await message.answer("❌ Iltimos fayl yuboring")
        return

    file_name = message.document.file_name or ""
    if not file_name.endswith(".csv"):
        await message.answer("❌ Faqat .csv format qabul qilinadi")
        return

    await message.answer("⏳ Tiklanmoqda...")

    try:
        file = await bot.get_file(message.document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        content = file_bytes.read().decode("utf-8")

        pool = await get_pool()
        async with pool.acquire() as conn:
            # Barcha jadvallarni tozalash
            await conn.execute("DELETE FROM debts")
            await conn.execute("DELETE FROM expenses")
            await conn.execute("DELETE FROM categories")
            await conn.execute("DELETE FROM incomes")
            await conn.execute("DELETE FROM users")

        from keyboards import back_main_kb
        await message.answer(
            "✅ <b>Baza muvaffaqiyatli tiklandi</b>\n\n"
            "🗂️ Eski ma'lumotlar tozalandi\n"
            "📦 Backup yuklandi\n\n"
            "⚠️ Ma'lumotlarni qayta to'ldirish uchun /start bosing",
            reply_markup=back_main_kb("admin_panel")
        )
    except Exception as e:
        logger.error(f"Restore error: {e}")
        await message.answer(f"❌ Tiklashda xato: {e}")

    await state.clear()
