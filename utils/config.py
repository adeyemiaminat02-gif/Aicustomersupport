import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
    AI_API_KEY = os.getenv("AI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
    DATABASE_URL = os.getenv("DATABASE_URL", "data/bot_database.db")
    PORT = int(os.getenv("PORT", 8000))
    
    # Parse comma-separated admin IDs
    admin_raw = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(x.strip()) for x in admin_raw.split(",") if x.strip().isdigit()]

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is missing.")
        if not cls.AI_API_KEY:
            raise ValueError("AI_API_KEY environment variable is missing.")
