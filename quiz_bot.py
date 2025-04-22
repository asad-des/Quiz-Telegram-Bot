import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging konfiguratsiyasi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Savollar va javoblar
questions = [
    {"question": "1-savol: Telegram dasturi qachon ishga tushirilgan?", "answer": "2013-yil", "options": ["2010-yil", "2011-yil", "2012-yil", "2013-yil"]},
    {"question": "2-savol: Telegram asoschisi kim?", "answer": "Pavel Durov", "options": ["Mark Zuckerberg", "Pavel Durov", "Elon Musk", "Jeff Bezos"]},
    {"question": "3-savol: Telegramning asosiy funksiyalari qaysilar?", "answer": "Xabar yuborish, guruhlar, kanallar, botlar", "options": ["Xabar yuborish, rasm yuborish", "Guruhlar, kanallar, botlar", "Video konferensiyalar", "Xabar yuborish, guruhlar, kanallar, botlar"]},
    {"question": "4-savol: Telegramda qancha odam bir guruhda bo'lishi mumkin?", "answer": "200,000", "options": ["10,000", "50,000", "200,000", "500,000"]},
    {"question": "5-savol: Telegramda o'z xabaringizni qaysi formatda yuborishingiz mumkin?", "answer": "Matn, rasm, video, fayl, ovozli xabar", "options": ["Matn, rasm, video", "Matn, rasm, video, fayl", "Matn, video, ovozli xabar", "Matn, rasm, video, fayl, ovozli xabar"]},
    {"question": "6-savol: Telegramda xabarlar necha kunga saqlanadi?", "answer": "Cheksiz vaqtga", "options": ["Bir oy", "Bir hafta", "Cheksiz vaqtga", "Bir yil"]},
    {"question": "7-savol: Telegramda 'BotFather' nima?", "answer": "Bot yaratish uchun Telegramning rasmiy botidir", "options": ["Telegram boti", "Bot yaratish uchun Telegramning rasmiy botidir", "Yordamchi bot", "Adminga bot"]},
    {"question": "8-savol: Telegramda shaxsiy suhbatlar uchun xavfsizlikni qanday ta'minlash mumkin?", "answer": "End-to-end shifrlash, maxfiy suhbatlar", "options": ["End-to-end shifrlash", "Maxfiy suhbatlar", "Ikkala variant ham", "Foydalanuvchi ruxsati"]},
    {"question": "9-savol: Telegram kanallarining qanday turlari mavjud?", "answer": "Ommaviy va maxfiy kanallar", "options": ["Ommaviy va maxfiy kanallar", "Foydalanuvchi va maxfiy kanallar", "Ommaviy kanallar", "Shaxsiy va ommaviy kanallar"]},
    {"question": "10-savol: Telegramda biror bir guruhni admin qilish uchun qanday ruxsat kerak?", "answer": "Admin huquqlari kerak", "options": ["Foydalanuvchi huquqlari", "Admin huquqlari kerak", "Ruxsatnoma", "Moderatsiya huquqlari"]}
]

# Har bir foydalanuvchi uchun individual holat
user_data = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🧪 Testni boshlash", callback_data="start_quiz")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="👋 Assalomu alaykum!\nTelegram test botiga xush kelibsiz!",
        reply_markup=reply_markup
    )

# Testni boshlash
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data[user_id] = {"question_index": 0, "correct": 0}
    await send_question(query, context)

# Savol yuborish
async def send_question(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    user_id = update_or_query.from_user.id
    q_index = user_data[user_id]["question_index"]
    question = questions[q_index]

    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=opt)]
        for opt in question["options"]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await context.bot.send_message(
        chat_id=update_or_query.message.chat.id if hasattr(update_or_query, "message") else update_or_query.effective_chat.id,
        text=f"{question['question']}",
        reply_markup=reply_markup
    )

# Callback — foydalanuvchi variant tanlaganda
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = user_data.get(user_id)

    if data is None:
        return await query.edit_message_text("Iltimos, /start buyrug‘ini yuboring.")

    q_index = data["question_index"]
    selected = query.data
    correct = questions[q_index]["answer"]

    if selected == correct:
        data["correct"] += 1
        await query.edit_message_text(f"✅ To'g'ri javob: {selected}")
    else:
        await query.edit_message_text(f"❌ Noto‘g‘ri! To‘g‘ri javob: {correct}")

    data["question_index"] += 1
    if data["question_index"] < len(questions):
        await send_question(query, context)
    else:
        score = data["correct"]
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Qayta boshlash", callback_data="start_quiz")]])
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"🎉 Quiz tugadi!\n✅ To‘g‘ri javoblar soni: {score} / {len(questions)}",
            reply_markup=reply_markup
        )

# Botni ishga tushurish
if __name__ == '__main__':
    app = Application.builder().token("7726793499:AAFZkg95be-568rAuEYZzNUhVMQE2cU6mTA").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_quiz, pattern="^start_quiz$"))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^(?!start_quiz).+"))

    app.run_polling()
