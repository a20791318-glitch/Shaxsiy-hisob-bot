# 📊 Shaxsiy Hisob Bot

Telegram bot — kirim, xarajat, qarz va hisobotlarni yuritish uchun.

---

## 🚀 Render.com ga Deploy qilish

### 1. PostgreSQL Database yaratish
1. [render.com](https://render.com) ga kiring
2. **New → PostgreSQL** bosing
3. Name: `hisob-db`
4. Plan: **Free**
5. **Create Database** bosing
6. `Internal Database URL` ni nusxa oling (keyinchalik kerak bo'ladi)

### 2. Bot yaratish
1. **New → Web Service** bosing
2. GitHub reponi ulang yoki **Deploy from existing repo** tanlang
3. Settings:
   - **Name**: `hisob-bot`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free

### 3. Environment Variables qo'shish
`Environment` bo'limiga quyidagilarni kiriting:

| Key | Value |
|-----|-------|
| `BOT_TOKEN` | BotFather dan olingan token |
| `ADMIN_IDS` | Admin Telegram ID lari (vergul bilan: `123456,789012`) |
| `CHANNEL_USERNAME` | `@my_botstg` |
| `DATABASE_URL` | PostgreSQL Internal URL (2-qadamdan) |
| `PORT` | `10000` |

### 4. Deploy
**Create Web Service** bosing → bot o'zi deploy bo'ladi.

---

## ⚙️ Local ishga tushirish

```bash
# 1. O'rnatish
pip install -r requirements.txt

# 2. .env fayl yaratish
cp .env.example .env
# .env faylni to'ldiring

# 3. Ishga tushirish
python bot.py
```

---

## 📁 Loyiha tuzilishi

```
hisob_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Konfiguratsiya
├── keep_alive.py       # Render uchun HTTP server
├── requirements.txt
├── render.yaml         # Render config
├── .env.example
├── database/
│   └── db.py           # PostgreSQL funksiyalar
├── handlers/
│   ├── start.py        # /start, obuna tekshirish
│   ├── income.py       # Kirim moduli
│   ├── expense.py      # Xarajat moduli
│   ├── debt.py         # Qarz moduli
│   ├── report.py       # Hisobot moduli
│   ├── help_module.py  # Yordam / Support
│   ├── settings.py     # Sozlamalar
│   └── admin.py        # Admin panel
├── keyboards/
│   └── __init__.py     # Barcha inline keyboard lar
└── states/
    └── __init__.py     # FSM state lar
```

---

## 🔧 Funksiyalar

- ✅ Majburiy obuna tekshirish
- ✅ Kirim: Naqd, Karta, Valyuta (USD/EUR/UZS)
- ✅ Xarajat: Dynamic kategoriyalar
- ✅ Qarz olish / berish, qisman to'lov
- ✅ Haftalik / Oylik hisobot
- ✅ Support tizimi (admin javob berishi mumkin)
- ✅ Sozlamalar: valyuta, ma'lumotlarni tozalash
- ✅ Admin panel: statistika, broadcast, backup
- ✅ PostgreSQL (Render free tier)
- ✅ Health check HTTP server (Render port)

---

## ⚠️ Muhim

Render free tier har 15 daqiqada bot so'rov bo'lmasa uxlab qoladi.
Buning oldini olish uchun [UptimeRobot](https://uptimerobot.com) dan foydalaning:
- URL: `https://your-app.onrender.com`
- Interval: 5 daqiqa
