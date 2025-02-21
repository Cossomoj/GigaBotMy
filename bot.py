import telebot
from telebot import types
from gigachat import GigaChat
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ваш API-токен GigaChat
def ask_gigachat(question):
    API_TOKEN = "NzU0ZjA2NzctYjlmOC00M2UxLWExNWQtNmQwNTIxMjg1Yzc3OmZlMTNiZGEzLTc2MzgtNGExZS1hODY5LTA3MGRmNTU2MTgyNg=="
    try:
        giga = GigaChat(credentials=API_TOKEN, verify_ssl_certs=False)
        response = giga.chat(question)
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при запросе к GigaChat: {e}")
        return "Произошла ошибка при получении ответа. Попробуйте еще раз."

# Вставьте сюда ваш токен
bot = telebot.TeleBot("7302486009:AAEjvjmgyeqFU2Hd_KgL5SgHmwAtKL0O1Q0")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f"Пользователь {message.chat.id} отправил команду /start")
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Start", callback_data="start")
    markup.add(button)
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку ниже, чтобы начать:", reply_markup=markup)

@bot.message_handler(commands=['menu'])
def handle_menu(message):
    logger.info(f"Пользователь {message.chat.id} отправил команду /menu")
    bot.send_message(message.chat.id, "Выберите роль")

@bot.callback_query_handler(func=lambda call: call.data == "start")
def handle_start(call):
    logger.info(f"Пользователь {call.message.chat.id} нажал кнопку Start")
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Menu", callback_data="menu")
    markup.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы нажали Start!")
    bot.send_message(call.message.chat.id, "Теперь вы можете продолжить использовать бота.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "menu")
def handle_menu(call):
    logger.info(f"Пользователь {call.message.chat.id} открыл меню выбора роли")
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="SA", callback_data="sa")
    markup.add(button)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите роль", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "sa")
def handle_sa(call):
    logger.info(f"Пользователь {call.message.chat.id} выбрал роль SA")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите ваш вопрос")
    bot.register_next_step_handler(call.message, process_question)

def process_question(message):
    logger.info(f"Пользователь {message.chat.id} задал вопрос: {message.text}")
    answer = ask_gigachat(message.text)
    bot.send_message(message.chat.id, answer)
    send_welcome(message)

try:
    logger.info("Бот запущен и работает...")
    bot.polling(none_stop=True)
except Exception as e:
    logger.critical(f"Критическая ошибка в работе бота: {e}", exc_info=True)
