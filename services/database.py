import os
import aiosqlite
from utils.config import Config
from utils.logger import logger

class DatabaseService:
    def __init__(self):
        self.db_path = Config.DATABASE_URL
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    language TEXT DEFAULT 'en',
                    style TEXT DEFAULT 'Balanced',
                    history_enabled INTEGER DEFAULT 1
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    email TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'Open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id INTEGER,
                    rating TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
            logger.info("Database initialized successfully.")

    async def get_user_settings(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT language, style, history_enabled FROM users WHERE user_id = ?", (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {"language": row[0], "style": row[1], "history_enabled": bool(row[2])}
                else:
                    await db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                    await db.commit()
                    return {"language": "en", "style": "Balanced", "history_enabled": True}

    async def update_user_setting(self, user_id: int, column: str, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
            await db.commit()

    async def save_ticket(self, user_id: int, name: str, email: str, desc: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO tickets (user_id, name, email, description) VALUES (?, ?, ?, ?)",
                (user_id, name, email, desc)
            )
            await db.commit()

    async def log_conversation(self, user_id: int, role: str, content: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
            await db.commit()
            # Trim history to maintain last 20 messages per session
            await db.execute("""
                DELETE FROM conversations WHERE id NOT IN (
                    SELECT id FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 20
                ) AND user_id = ?
            """, (user_id, user_id))
            await db.commit()

    async def get_conversation_history(self, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT role, content FROM conversations WHERE user_id = ? ORDER BY created_at ASC", (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [{"role": r[0], "content": r[1]} for r in rows]

    async def save_feedback(self, user_id: int, rating: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO feedback (user_id, rating) VALUES (?, ?)", (user_id, rating))
            await db.commit()

    async def get_open_tickets(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT id, user_id, name, description FROM tickets WHERE status = 'Open'") as cursor:
                return await cursor.fetchall()

db_service = DatabaseService()
