import telebot from telebot import types import requests import logging

Настройка логирования

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') logger = logging.getLogger(name)

Токен Telegram бота

BOT_TOKEN = "ВАШ_ТГ_ТОКЕН" RAG_API_URL = "http://127.0.0.1:8000/search/"  # URL микросервиса

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start']) def send_welcome(message): logger.info(f"Пользователь {message.chat.id} отправил команду /start") markup = types.InlineKeyboardMarkup() button = types.InlineKeyboardButton(text="Start", callback_data="start") markup.add(button) bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку ниже, чтобы начать:", reply_markup=markup)

@bot.message_handler(commands=['menu']) def handle_menu(message): logger.info(f"Пользователь {message.chat.id} отправил команду /menu") bot.send_message(message.chat.id, "Выберите роль")

@bot.callback_query_handler(func=lambda call: call.data == "start") def handle_start(call): logger.info(f"Пользователь {call.message.chat.id} нажал кнопку Start") bot.send_message(call.message.chat.id, "Введите ваш вопрос:") bot.register_next_step_handler(call.message, process_question)

@bot.callback_query_handler(func=lambda call: call.data == "menu") def handle_menu(call): logger.info(f"Пользователь {call.message.chat.id} открыл меню выбора роли") markup = types.InlineKeyboardMarkup() button = types.InlineKeyboardButton(text="SA", callback_data="sa") markup.add(button) bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите роль", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "sa") def handle_sa(call): logger.info(f"Пользователь {call.message.chat.id} выбрал роль SA") bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите ваш вопрос") bot.register_next_step_handler(call.message, process_question)

def process_question(message): logger.info(f"Пользователь {message.chat.id} задал вопрос: {message.text}") try: response = requests.post(RAG_API_URL, json={"query": message.text, "k": 3}) response_data = response.json() if "matches" in response_data: answer = "\n".join(response_data["matches"]) else: answer = "Не удалось найти релевантную информацию." except Exception as e: logger.error(f"Ошибка при запросе к RAG API: {e}") answer = "Ошибка обработки запроса." bot.send_message(message.chat.id, answer) send_welcome(message)

try: logger.info("Бот запущен и работает...") bot.polling(none_stop=True) except Exception as e: logger.critical(f"Критическая ошибка в работе бота: {e}", exc_info=True)

