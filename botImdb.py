from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import asyncio
from randomIMDB import get_top_movies, getMoviesfromDirector  # Импортируем необходимые функции

# Настроим логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update, context):
    await update.message.reply_text(
        'Hello! Use the commands below to interact with me:\n'
        '/start - Start the bot\n'
        '/name <name> - Get movies from a director\n'
        '\nClick below to get the top movies list:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Get Top 250 Movies", callback_data='get_movies')]
        ])
    )

# Команда /director
# Команда /director
async def director(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide the name. Usage: /name <name>")
        return

    # Получаем имя режиссёра из аргументов
    director_name = " ".join(context.args)
    await update.message.reply_text(f"Searching for movies by {director_name}... Please wait.")

    # Вызываем функцию парсинга фильмов по имени режиссёра
    try:
        movies = getMoviesfromDirector(director_name)
        formatted_movies = []
        if not movies:
            await update.message.reply_text(f"No movies found for name: {director_name}")
        else:
            for movie in movies:
                # Примерная структура данных фильма: (Название, Год, Рейтинг, URL)
                title, year, url = movie["title"], movie["year"], movie["url"]

                # Формируем строку с гиперссылкой в Markdown
                movie_message = f"*{title}* {year} [Link]({url})"
                formatted_movies.append(movie_message)

            # Разбиваем список на части по 60 фильмов
            chunk_size = 60
            for i in range(0, len(formatted_movies), chunk_size):
                # Формируем одно сообщение с 60 фильмами
                chunk = formatted_movies[i:i+chunk_size]
                message = f"Here are the movies by {director_name}:\n\n" + "\n".join(chunk)

                # Отправляем новое сообщение
                await context.bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)

                # Добавляем паузу в 1 секунду между сообщениями
                await asyncio.sleep(1)  # Можно настроить время паузы по необходимости

    except Exception as e:
        logger.error(f"Error fetching movies for director {director_name}: {e}")
        await update.message.reply_text("An error occurred while fetching the movies. Please try again later.")




# Обработка нажатия кнопки
async def button(update, context):
    query = update.callback_query
    await query.answer()

    # Заменяем кнопку на "Wait"
    await query.edit_message_text(text="Please wait, fetching the top movies...",
                                  reply_markup=InlineKeyboardMarkup([
                                      [InlineKeyboardButton("Wait", callback_data='wait')]
                                  ]))

    # Получаем топ фильмов
    movies = get_top_movies()

    # Отладочный вывод
    print(f"Movies retrieved: {movies}")  # Выведем список фильмов в консоль

    if not movies:
        await query.edit_message_text(text="Sorry, I couldn't retrieve the top movies at this time.")
    else:
        # Формируем сообщение с форматированием
        formatted_movies = []
        for movie in movies:
            # Примерная структура данных фильма: (Название, Год, Рейтинг, URL)
            title, year, rating, url = movie["title"], movie["year"], movie["rating"], movie["url"]

            # Формируем строку с гиперссылкой в Markdown
            movie_message = f"*{title}* ({year})\nRating: {rating}\n[Link]({url})"
            formatted_movies.append(movie_message)

        # Разбиваем список на части по 60 фильмов
        chunk_size = 60
        for i in range(0, len(formatted_movies), chunk_size):
            # Формируем одно сообщение с 60 фильмами
            chunk = formatted_movies[i:i+chunk_size]
            message = "Here are the top movies:\n\n" + "\n\n".join(chunk)

            # Отправляем новое сообщение
            await context.bot.send_message(chat_id=query.message.chat_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)

            # Добавляем паузу в 1 секунду между сообщениями
            await asyncio.sleep(1)  # Можно настроить время паузы по необходимости

def main():
    # Замените YOUR_TOKEN на ваш токен
    application = Application.builder().token("YOU TOKEN").build()

    # Регистрируем команду /start
    application.add_handler(CommandHandler("start", start))

    # Регистрируем команду /director
    application.add_handler(CommandHandler("name", director))

    # Регистрируем обработчик кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
