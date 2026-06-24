from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from states import SupportState, SupportReplyState
from keyboards import help_menu_kb, after_support_kb, admin_reply_kb, back_main_kb

router = Router()


@router.callback_query(F.data == "help_menu")
async def help_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "🆘 <b>Yordam bo'limi</b>\n\n"
        "Ushbu bot orqali siz:\n\n"
        "💰 Kirimlarni yozishingiz\n"
        "➖ Xarajatlarni hisoblab borishingiz\n"
        "🏡 Uyga yuborilgan pullarni saqlashingiz\n"
        "🤝 Qarzlarni boshqarishingiz\n"
        "📊 Haftalik/Oylik hisobotlarni ko'rishingiz\n\n"
        "mumkin.\n\n"
        "Agar sizda savol, muammo, taklif yoki shikoyat bo'lsa admin bilan bog'lanishingiz mumkin 👇",
        reply_markup=help_menu_kb()
    )
    await call.answer()


@router.callback_query(F.data == "support_write")
async def support_write(call: CallbackQuery, state: FSMContext):
    await state.set_state(SupportState.message)
    await call.message.edit_text(
        "✍️ <b>Xabaringizni yuboring:</b>\n\n"
        "📌 Matn, rasm, video yoki fayl yuborishingiz mumkin."
    )
    await call.answer()


@router.message(SupportState.message)
async def process_support_message(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    name = f"{user.first_name} {user.last_name or ''}".strip()

    admin_text = (
        f"📨 <b>YANGI MUROJAAT</b>\n\n"
        f"👤 User: <a href='tg://user?id={user.id}'>{name}</a>\n"
        f"🆔 ID: <code>{user.id}</code>\n\n"
        f"💬 Xabar:\n"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=admin_reply_kb(user.id))
            # Forward original message (rasm/video/fayl bo'lsa)
            await message.forward(admin_id)
        except Exception:
            pass

    await message.answer(
        "✅ <b>Xabaringiz adminga yuborildi</b>\n\n📨 Tez orada javob olasiz.",
        reply_markup=after_support_kb()
    )
    await state.clear()


@router.callback_query(F.data.startswith("support_reply_"))
async def support_reply(call: CallbackQuery, state: FSMContext):
    user_id = int(call.data.split("_")[-1])
    await state.set_state(SupportReplyState.message)
    await state.update_data(target_user_id=user_id)
    await call.message.edit_text("✍️ <b>Userga yuboriladigan javobni kiriting:</b>")
    await call.answer()


@router.message(SupportReplyState.message)
async def process_support_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_id = data.get("target_user_id")
    try:
        await bot.send_message(
            target_id,
            f"📨 <b>Admin javobi:</b>\n\n{message.text}",
            reply_markup=after_support_kb()
        )
        await message.answer("✅ Javob yuborildi")
    except Exception:
        await message.answer("❌ Xabar yuborishda xato")
    await state.clear()


@router.callback_query(F.data.startswith("support_close_"))
async def support_close(call: CallbackQuery):
    await call.message.edit_text("✅ Murojaat yopildi")
    await call.answer()
