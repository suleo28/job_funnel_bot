import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

VACANCIES, QUESTIONS, FINAL = range(3)

vacancies = {
    "🔧 Сборщик": "Работа на производстве. Требуется внимательность и аккуратность.",
    "📦 Комплектовщик": "Работа на складе. Упаковка и сортировка товаров.",
    "🚚 Курьер": "Доставка заказов по городу. Желателен личный транспорт.",
    "🧹 Уборщик": "Уборка офисов и помещений. Гибкий график."
}

questions = [
    "Сколько вам лет?",
    "Есть ли опыт по этой вакансии?",
    "Готовы ли работать в ночную смену?",
    "Можете ли приступить в ближайшие 3 дня?"
]

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[k] for k in vacancies.keys()]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Привет! Какая вакансия вас интересует?", reply_markup=markup)
    return VACANCIES

async def choose_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vacancy = update.message.text
    context.user_data['vacancy'] = vacancy
    await update.message.reply_text(
    f"{vacancy}:\n{vacancies[vacancy]}\n\nПодходит ли вам эта вакансия? (Да/Нет)"
)
    return QUESTIONS

async def ask_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() != "да":
        await update.message.reply_text("Хорошо. Можете выбрать другую вакансию командой /start.")
        return ConversationHandler.END

    context.user_data['answers'] = []
    context.user_data['q_index'] = 0
    await update.message.reply_text(questions[0])
    return FINAL

async def collect_answers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text
    context.user_data['answers'].append(answer)

    # Отсев по возрасту
    if context.user_data['q_index'] == 0:
        try:
            if int(answer) < 18:
                await update.message.reply_text("Извините, вы не подходите по возрасту.")
                return ConversationHandler.END
        except:
            await update.message.reply_text("Пожалуйста, введите возраст числом.")
            return FINAL

    context.user_data['q_index'] += 1
    if context.user_data['q_index'] < len(questions):
        await update.message.reply_text(questions[context.user_data['q_index']])
        return FINAL
    else:
        summary = "\n".join(
            f"{questions[i]} {ans}" for i, ans in enumerate(context.user_data['answers'])
        )
        await update.message.reply_text(f"Спасибо за ответы!\n\nВакансия: {context.user_data['vacancy']}\n{summary}\n\nМы передадим ваши данные менеджеру.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог завершён.")
    return ConversationHandler.END

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VACANCIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_vacancy)],
            QUESTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_questions)],
            FINAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_answers)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
