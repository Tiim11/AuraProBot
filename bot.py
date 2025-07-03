import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv
from ml_engine import FAQAnswerEngine

# Загрузка .env
load_dotenv()

# Загрузка токена из переменных окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Расширенный FAQ
FAQ = {
    "connect": {
        "question": "Как подключить наушники?",
        "answer": (
            "1. Включите Bluetooth на телефоне.\n"
            "2. Откройте кейс рядом с устройством.\n"
            "3. Зажмите кнопку на кейсе до мигания индикатора.\n"
            "4. Выберите 'AirPods Pro' в настройках Bluetooth.\n\n"
            "_На Android подключение вручную через Bluetooth_"
        )
    },
    "battery": {
        "question": "Как узнать уровень заряда?",
        "answer": (
            "- \ud83d\udcf1 iPhone: откройте кейс рядом с телефоном — отобразится окно.\n"
            "- \ud83d\udfe2 Зеленый индикатор — заряд полный, \ud83d\udfe0 Оранжевый — менее 100%.\n"
            "- \ud83d\udcf2 Android: уровень заряда виден в шторке или через приложения (AirBattery, MaterialPods)."
        )
    },
    "one_airpod": {
        "question": "Работает только один наушник",
        "answer": (
            "1. Проверьте, что оба наушника заряжены.\n"
            "2. Очистите контакты в кейсе.\n"
            "3. Сбросьте и повторно подключите.\n"
            "4. Используйте один наушник, затем подключите второй — может помочь синхронизации."
        )
    },
    "sound": {
        "question": "Проблемы со звуком",
        "answer": (
            "1. Проверьте громкость на телефоне.\n"
            "2. Очистите сетки динамиков.\n"
            "3. Попробуйте другое устройство.\n"
            "4. Зарядите наушники полностью."
        )
    },
    "discharge": {
        "question": "Быстро разряжаются",
        "answer": (
            "1. Отключите шумоподавление, если не требуется.\n"
            "2. Убедитесь, что наушники кладутся в кейс.\n"
            "3. Не оставляйте подключёнными в фоновом режиме.\n"
            "4. Заряд держится 3–5 часов в зависимости от режима."
        )
    },
    "sensor": {
        "question": "Не срабатывает сенсор нажатия",
        "answer": (
            "1. Очистите поверхность ножки наушника.\n"
            "2. Попробуйте нажимать чуть ниже середины ножки.\n"
            "3. Проверьте настройки управления в телефоне.\n"
            "4. На Android функции могут быть ограничены — это нормально."
        )
    },
    "mic": {
        "question": "Проблемы с микрофоном",
        "answer": (
            "1. Протрите микрофоны на ножке.\n"
            "2. В настройках выберите левый или правый микрофон.\n"
            "3. Убедитесь, что приложению разрешён доступ к микрофону."
        )
    },
    "noise_control": {
        "question": "Как управлять шумоподавлением?",
        "answer": (
            "- На iPhone: удерживайте ножку наушника или через «Центр управления».\n"
            "- Режимы: *Шумоподавление*, *Прозрачность*, *Отключено*.\n"
            "- На Android: поддерживается не всегда, зависит от прошивки."
        )
    },
    "charging_case": {
        "question": "Что означает мигание индикатора на кейсе?",
        "answer": (
            "- \ud83d\udfe2 Зеленый — кейс заряжен.\n"
            "- \ud83d\udfe0 Оранжевый — заряд менее 100%.\n"
            "- ⚪ Белый мигает — режим сопряжения.\n"
            "- 🔴 Красный — возможно, ошибка или разряд. Зарядите кейс."
        )
    },
    "reset": {
        "question": "Как сбросить настройки наушников?",
        "answer": (
            "1. Удалите наушники из Bluetooth-устройств на телефоне.\n"
            "2. Положите наушники в кейс и закройте на 15 сек.\n"
            "3. Откройте кейс и удерживайте кнопку на нем 15 сек, пока индикатор не мигнёт оранжевым, затем белым.\n"
            "4. Подключите наушники заново — они сброшены."
        )
    },
    "care": {
        "question": "Как ухаживать за наушниками?",
        "answer": (
            "🧼 Чистите мягкой сухой щёткой.\n"
            "🚫 Не используйте воду, спирт или компрессоры.\n"
            "⚡ Заряжайте регулярно, не допускайте глубокого разряда.\n"
            "📦 Храните в кейсе — это защищает и продлевает срок службы."
        )
    }
}

engine = FAQAnswerEngine(FAQ)

# Логирование
def log_user_action(user_id: int, username: str, query: str):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{time}] User {username} (ID: {user_id}) → {query}\n"
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(log_line)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔌 Подключение", callback_data="connect"),
         InlineKeyboardButton("🔋 Заряд", callback_data="battery")],
        [InlineKeyboardButton("🎧 Один наушник", callback_data="one_airpod"),
         InlineKeyboardButton("🔊 Проблемы со звуком", callback_data="sound")],
        [InlineKeyboardButton("⚡ Быстрый разряд", callback_data="discharge"),
         InlineKeyboardButton("📶 Шумоподавление", callback_data="noise_control")],
        [InlineKeyboardButton("🛠️ Сброс настроек", callback_data="reset"),
         InlineKeyboardButton("🎙️ Микрофон", callback_data="mic")],
        [InlineKeyboardButton("🤏 Сенсор управления", callback_data="sensor"),
         InlineKeyboardButton("💡 Уход", callback_data="care")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать! Я бот техподдержки AirPods Pro 2.\n\nВыберите вопрос из списка ниже:",
        reply_markup=reply_markup
    )

# Обработка нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    faq_id = query.data
    faq = FAQ.get(faq_id)
    if faq:
        user = query.from_user
        log_user_action(user.id, user.username or "NoUsername", faq["question"])
        await query.message.reply_text(
            f"❓ *{faq['question']}*\n\n{faq['answer']}",
            parse_mode="Markdown"
        )

# Обработка произвольных сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user = update.message.from_user
    question, answer = engine.find_best_match(user_input)
    if answer:
        log_user_action(user.id, user.username or "NoUsername", f"ML-match: {question}")
        await update.message.reply_text(
            f"❓ *{question}*\n\n{answer}", parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "🤖 Я не уверен, как ответить. Попробуйте выбрать из /start или переформулируйте."
        )
        log_user_action(user.id, user.username or "NoUsername", f"ML-no-match: {user_input}")

# Запуск приложения
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Бот запущен")
    app.run_polling()
