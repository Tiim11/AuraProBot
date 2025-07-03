import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from ml_engine import FAQAnswerEngine

FAQ = {
    "connect": {"question": "Как подключить наушники?", "answer": "Откройте кейс и подключите через Bluetooth..."},
    "reset": {"question": "Как сбросить настройки?", "answer": "Удерживайте кнопку на кейсе 15 секунд..."}
    # Добавь остальные вопросы
}

engine = FAQAnswerEngine(FAQ)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton(faq["question"], callback_data=key)] for key, faq in FAQ.items()]
    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("👋 Выберите вопрос:", reply_markup=markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq = FAQ.get(query.data)
    if faq:
        await query.message.reply_text(f"❓ {faq['question']}\n\n{faq['answer']}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q, a = engine.find_best_match(update.message.text)
    if a:
        await update.message.reply_text(f"❓ {q}\n\n{a}")
    else:
        await update.message.reply_text("🤖 Я не совсем понял вопрос. Попробуйте иначе или нажмите /start.")

if __name__ == "__main__":
    import logging
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
