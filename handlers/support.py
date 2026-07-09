from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.database import db_service

NAME, EMAIL, DESC = range(3)

async def start_support_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query
    text = "🎫 *Initiating Support Ticket*\n\nLet's compile details. Please send your text name, or submit `/skip` to remain private:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")
    return NAME

async def ticket_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    context.user_data["ticket_name"] = "Anonymous" if val.lower() == "/skip" else val
    await update.message.reply_text("📩 Perfect. Please provide your Email Address, or submit `/skip`:")
    return EMAIL

async def ticket_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text
    context.user_data["ticket_email"] = "Not Provided" if val.lower() == "/skip" else val
    await update.message.reply_text("📝 Please outline your descriptive problem with complete transparency:")
    return DESC

async def ticket_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    desc = update.message.text
    name = context.user_data.get("ticket_name", "Anonymous")
    email = context.user_data.get("ticket_email", "Not Provided")

    await db_service.save_ticket(user_id, name, email, desc)
    
    await update.message.reply_text(
        f"✅ *Ticket Logged Successfully!*\n"
        f"Our engineering and support branch has been auto-notified. "
        f"Your dynamic reference ticket tracking state is now active."
    )
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Ticket generation processes aborted.")
    context.user_data.clear()
    return ConversationHandler.END
