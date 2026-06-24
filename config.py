import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@my_botstg")
DATABASE_URL = os.getenv("DATABASE_URL", "")
PORT = int(os.getenv("PORT", 10000))

# Admin IDlari vergul bilan ajratilgan
_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in _admin_ids.split(",") if x.strip().isdigit()]

CURRENCY_SYMBOLS = {
    "RUB": "₽",
    "USD": "$",
    "UZS": "so'm",
    "EUR": "€",
}

CURRENCY_RATES = {
    "USD": 89.0,
    "EUR": 96.0,
    "UZS": 0.0078,
    "RUB": 1.0,
}
