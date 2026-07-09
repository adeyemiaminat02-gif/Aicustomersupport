import json
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.inline import get_faq_menu

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 *Frequently Asked Questions*\nSelect a segment below to query stored responses."
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_faq_menu())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=get_faq_menu())

async def faq_routing_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    with open("data/knowledge_base.json", "r") as f:
        kb = json.load(f)

    mapping = {
        "faq_hours": ("🕒 Business Hours", kb.get("business_hours")),
        "faq_pricing": ("💰 Pricing Matrix", kb.get("pricing")),
        "faq_refund": ("📦 Refund Assurance", kb.get("refund_policy"))
    }

    title, content = mapping.get(query.data, ("Info", "No structured content data found."))
    response_text = f"*{title}*\n\n{content}"
    
    await query.edit_message_text(response_text, parse_mode="Markdown", reply_markup=get_faq_menu())
