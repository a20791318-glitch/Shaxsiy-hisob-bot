from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_kb(is_admin=False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="➕ Kirim", callback_data="income_menu"),
            InlineKeyboardButton(text="➖ Xarajat", callback_data="expense_menu"),
        ],
        [
            InlineKeyboardButton(text="🤝 Qarz", callback_data="debt_menu"),
            InlineKeyboardButton(text="📊 Hisobot", callback_data="report_menu"),
        ],
        [
            InlineKeyboardButton(text="📢 Ulashish", callback_data="share"),
            InlineKeyboardButton(text="🆘 Yordam", callback_data="help_menu"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings_menu"),
        ],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="👨🏻‍💻 Admin panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_main_kb(back_cb: str = None) -> InlineKeyboardMarkup:
    """Orqaga va Asosiy Menu tugmalari"""
    buttons = []
    if back_cb:
        buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_cb)])
    buttons.append([InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscribe_kb() -> InlineKeyboardMarkup:
    from config import CHANNEL_USERNAME
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Obuna bo'lish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")],
    ])


def currency_select_kb(back_cb="settings_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 RUB ₽", callback_data="currency_rub"),
            InlineKeyboardButton(text="🇺🇸 USD $", callback_data="currency_usd"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 UZS so'm", callback_data="currency_uzs"),
            InlineKeyboardButton(text="🇪🇺 EUR €", callback_data="currency_eur"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=back_cb)],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def income_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 Naqd", callback_data="income_cash"),
            InlineKeyboardButton(text="💳 Karta", callback_data="income_card"),
        ],
        [
            InlineKeyboardButton(text="🪙 Valyuta", callback_data="income_currency"),
            InlineKeyboardButton(text="📋 Kirim tarixi", callback_data="income_history"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def income_currency_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 USD", callback_data="income_usd"),
            InlineKeyboardButton(text="💶 EUR", callback_data="income_eur"),
        ],
        [
            InlineKeyboardButton(text="🇺🇿 UZS", callback_data="income_uzs"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="income_menu")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def after_income_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="income_menu")],
        [InlineKeyboardButton(text="📋 Kirim tarixi", callback_data="income_history")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def expense_menu_kb(categories) -> InlineKeyboardMarkup:
    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(text=cat["name"], callback_data=f"expense_cat_{cat['id']}")])
    buttons.append([InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="expense_add_category")])
    buttons.append([InlineKeyboardButton(text="📋 Xarajat tarixi", callback_data="expense_history")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def expense_no_cat_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="expense_add_category")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def after_expense_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="expense_menu")],
        [InlineKeyboardButton(text="📂 Kategoriyalar", callback_data="expense_menu")],
        [InlineKeyboardButton(text="📋 Xarajat tarixi", callback_data="expense_history")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def debt_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📥 Qarz olish", callback_data="debt_take"),
            InlineKeyboardButton(text="📤 Qarz berish", callback_data="debt_give"),
        ],
        [
            InlineKeyboardButton(text="📋 Aktiv qarzlar", callback_data="debt_active"),
            InlineKeyboardButton(text="📜 Qarz tarixi", callback_data="debt_history"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def active_debts_kb(debts) -> InlineKeyboardMarkup:
    buttons = []
    for d in debts:
        icon = "📥" if d["type"] == "debt_taken" else "📤"
        text = f"{icon} {d['person']} — {d['remaining']:.0f}₽"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"debt_select_{d['id']}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="debt_menu")])
    buttons.append([InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def after_debt_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 To'lov qilish", callback_data="debt_pay_list")],
        [InlineKeyboardButton(text="📋 Aktiv qarzlar", callback_data="debt_active")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def debt_pay_list_kb(debts) -> InlineKeyboardMarkup:
    buttons = []
    for d in debts:
        icon = "📥" if d["type"] == "debt_taken" else "📤"
        text = f"{icon} {d['person']} — {d['remaining']:.0f}₽"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"debt_pay_{d['id']}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="debt_menu")])
    buttons.append([InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def report_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📅 Haftalik", callback_data="report_weekly"),
            InlineKeyboardButton(text="📆 Oylik", callback_data="report_monthly"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def help_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Adminga yozish", callback_data="support_write")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def settings_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💱 Valyutani o'zgartirish", callback_data="settings_currency")],
        [InlineKeyboardButton(text="🗑 Barcha ma'lumotlarni tozalash", callback_data="settings_clear")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def clear_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑 Tozalash", callback_data="clear_confirm"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="settings_menu"),
        ],
    ])


def clear_final_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data="clear_all"),
            InlineKeyboardButton(text="⬅️ Bekor qilish", callback_data="settings_menu"),
        ],
    ])


def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📤 Xabar yuborish", callback_data="admin_broadcast"),
        ],
        [
            InlineKeyboardButton(text="📁 Backup yuklash", callback_data="admin_backup"),
            InlineKeyboardButton(text="🗂️ Bazani tiklash", callback_data="admin_restore"),
        ],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="main_menu")],
    ])


def admin_stats_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Yangilash", callback_data="admin_stats")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_panel")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def admin_reply_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Javob berish", callback_data=f"support_reply_{user_id}")],
        [InlineKeyboardButton(text="🚫 Yopish", callback_data=f"support_close_{user_id}")],
    ])


def after_support_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Yana yozish", callback_data="support_write")],
        [InlineKeyboardButton(text="🏠 Asosiy Menu", callback_data="main_menu")],
    ])


def restore_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Davom etish", callback_data="restore_confirm")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")],
    ])
