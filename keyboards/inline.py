from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("💬 Ask a Question", callback_data="ask_question"),
         InlineKeyboardButton("📚 FAQs", callback_data="view_faqs")],
        [InlineKeyboardButton("🎫 Contact Support", callback_data="contact_support"),
         InlineKeyboardButton("⚙ Settings", callback_data="open_settings")],
        [InlineKeyboardButton("❓ Help", callback_data="view_help"),
         InlineKeyboardButton("ℹ About", callback_data="view_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_post_chat_menu():
    keyboard = [
        [InlineKeyboardButton("👍 Helpful", callback_data="rate_good"),
         InlineKeyboardButton("👎 Not Helpful", callback_data="rate_bad")],
        [InlineKeyboardButton("📚 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_faq_menu():
    keyboard = [
        [InlineKeyboardButton("🕒 Business Hours", callback_data="faq_hours"),
         InlineKeyboardButton("💰 Pricing Structure", callback_data="faq_pricing")],
        [InlineKeyboardButton("📦 Refund Policy", callback_data="faq_refund"),
         InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_menu(current_settings: dict):
    lang = current_settings['language'].upper()
    style = current_settings['style']
    hist = "ON" if current_settings['history_enabled'] else "OFF"
    
    keyboard = [
        [InlineKeyboardButton(f"🌐 Lang: {lang}", callback_data="toggle_lang"),
         InlineKeyboardButton(f"✍ Style: {style}", callback_data="toggle_style")],
        [InlineKeyboardButton(f"🧠 Context Memory: {hist}", callback_data="toggle_history")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
