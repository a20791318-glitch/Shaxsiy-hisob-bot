import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "")
_pool: asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                main_currency TEXT DEFAULT 'RUB',
                balance NUMERIC(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS incomes (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                type TEXT,
                amount NUMERIC(15,2),
                amount_original NUMERIC(15,2),
                currency TEXT DEFAULT 'RUB',
                rate NUMERIC(10,4) DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                category_id INT REFERENCES categories(id) ON DELETE SET NULL,
                category_name TEXT,
                amount NUMERIC(15,2),
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS debts (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                type TEXT,
                person TEXT,
                amount NUMERIC(15,2),
                paid NUMERIC(15,2) DEFAULT 0,
                remaining NUMERIC(15,2),
                comment TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    logger.info("Database initialized.")


async def get_or_create_user(user_id: int, first_name: str, last_name: str = None, username: str = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
        if not user:
            await conn.execute(
                "INSERT INTO users(user_id, first_name, last_name, username) VALUES($1,$2,$3,$4)",
                user_id, first_name, last_name, username
            )
            user = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
        return user


async def get_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)


async def set_user_currency(user_id: int, currency: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET main_currency=$1 WHERE user_id=$2", currency, user_id)


async def update_balance(user_id: int, amount: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET balance=balance+$1 WHERE user_id=$2", amount, user_id)


async def get_balance(user_id: int) -> float:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT balance FROM users WHERE user_id=$1", user_id)
        return float(row["balance"]) if row else 0.0


async def add_income(user_id: int, inc_type: str, amount: float, amount_orig: float, currency: str, rate: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO incomes(user_id, type, amount, amount_original, currency, rate) VALUES($1,$2,$3,$4,$5,$6)",
            user_id, inc_type, amount, amount_orig, currency, rate
        )
    await update_balance(user_id, amount)


async def get_recent_incomes(user_id: int, limit=10):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM incomes WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2",
            user_id, limit
        )


async def get_categories(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM categories WHERE user_id=$1 ORDER BY id", user_id)


async def add_category(user_id: int, name: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO categories(user_id, name) VALUES($1,$2) RETURNING id",
            user_id, name
        )
        return row["id"]


async def add_expense(user_id: int, category_id: int, category_name: str, amount: float):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO expenses(user_id, category_id, category_name, amount) VALUES($1,$2,$3,$4)",
            user_id, category_id, category_name, amount
        )
    await update_balance(user_id, -amount)


async def get_recent_expenses(user_id: int, limit=10):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM expenses WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2",
            user_id, limit
        )


async def add_debt(user_id: int, dtype: str, person: str, amount: float, comment: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO debts(user_id, type, person, amount, paid, remaining, comment) VALUES($1,$2,$3,$4,0,$4,$5)",
            user_id, dtype, person, amount, comment
        )
    if dtype == "debt_taken":
        await update_balance(user_id, amount)
    else:
        await update_balance(user_id, -amount)


async def get_active_debts(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM debts WHERE user_id=$1 AND status='active' ORDER BY created_at DESC",
            user_id
        )


async def get_all_debts(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM debts WHERE user_id=$1 ORDER BY created_at DESC",
            user_id
        )


async def get_debt_by_id(debt_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM debts WHERE id=$1", debt_id)


async def pay_debt(debt_id: int, amount: float, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        debt = await conn.fetchrow("SELECT * FROM debts WHERE id=$1", debt_id)
        new_paid = float(debt["paid"]) + amount
        new_remaining = float(debt["amount"]) - new_paid
        if new_remaining <= 0:
            new_remaining = 0
            status = "closed"
        else:
            status = "active"
        await conn.execute(
            "UPDATE debts SET paid=$1, remaining=$2, status=$3 WHERE id=$4",
            new_paid, new_remaining, status, debt_id
        )
        # Balansni o'zgartirish
        if debt["type"] == "debt_taken":
            await update_balance(user_id, -amount)
        else:
            await update_balance(user_id, amount)
        return new_remaining, status


async def clear_user_data(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM incomes WHERE user_id=$1", user_id)
        await conn.execute("DELETE FROM expenses WHERE user_id=$1", user_id)
        await conn.execute("DELETE FROM debts WHERE user_id=$1", user_id)
        await conn.execute("DELETE FROM categories WHERE user_id=$1", user_id)
        await conn.execute("UPDATE users SET balance=0 WHERE user_id=$1", user_id)


async def get_all_users():
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")


async def get_monthly_report(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        income_total = await conn.fetchval(
            "SELECT COALESCE(SUM(amount),0) FROM incomes WHERE user_id=$1 AND DATE_TRUNC('month', created_at)=DATE_TRUNC('month', NOW())",
            user_id
        )
        expense_total = await conn.fetchval(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=$1 AND DATE_TRUNC('month', created_at)=DATE_TRUNC('month', NOW())",
            user_id
        )
        cat_rows = await conn.fetch(
            """SELECT category_name, SUM(amount) as total FROM expenses 
               WHERE user_id=$1 AND DATE_TRUNC('month', created_at)=DATE_TRUNC('month', NOW())
               GROUP BY category_name ORDER BY total DESC""",
            user_id
        )
        return float(income_total), float(expense_total), cat_rows


async def get_weekly_report(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        income_total = await conn.fetchval(
            "SELECT COALESCE(SUM(amount),0) FROM incomes WHERE user_id=$1 AND created_at >= NOW() - INTERVAL '7 days'",
            user_id
        )
        expense_total = await conn.fetchval(
            "SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=$1 AND created_at >= NOW() - INTERVAL '7 days'",
            user_id
        )
        cat_rows = await conn.fetch(
            """SELECT category_name, SUM(amount) as total FROM expenses 
               WHERE user_id=$1 AND created_at >= NOW() - INTERVAL '7 days'
               GROUP BY category_name ORDER BY total DESC""",
            user_id
        )
        return float(income_total), float(expense_total), cat_rows
