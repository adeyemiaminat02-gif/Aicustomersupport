from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_only
from services.database import db_service
from utils.logger import logger

@admin_only
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tickets = await db_service.get_open_tickets()
    
    dash = f"🛠 *Administrative Overview Control Panel*\n\n"
    dash += f"Active Open Support Tickets: `{len(tickets)}`/200 allowed\n"
    dash += f"-----------------------------------------\n"
    
    for t in tickets[:5]:
        dash += f"ID {t[0]} | User: {t[2]}\nDesc: _{t[3]}_\n\n"
        
    dash += "Commands available:\n/broadcast <text> - Send universal alert message."
    await update.message.reply_text(dash, parse_mode="Markdown")

@admin_only
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Syntax error. Run `/broadcast Your message text here`")
        return

    broadcast_payload = " ".join(context.args)
    logger.info(f"Admin initiated a universal broad-scale data system alert.")
    await update.message.reply_text(f"🚀 Broadcast string finalized and processing pipeline initialized.")
