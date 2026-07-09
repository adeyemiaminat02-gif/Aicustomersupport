from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from utils.config import Config
from utils.logger import logger

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in Config.ADMIN_IDS:
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            if update.message:
                await update.message.reply_text("⛔ Access Denied. This command is restricted to administrators.")
            elif update.callback_query:
                await update.callback_query.answer("⛔ Access Denied.", show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
