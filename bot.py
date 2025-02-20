import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Твой API-токен от BotFather
TELEGRAM_BOT_TOKEN = "7302486009:AAEjvjmgyeqFU2Hd_KgL5SgHmwAtKL0O1Q0"

# API GigaChat (ключ авторизации и параметры)
GIGACHAT_CREDENTIALS = "NzU0ZjA2NzctYjlmOC00M2UxLWExNWQtNmQwNTIxMjg1Yzc3OjBiMjY2ZTIwLWI5YzQtNDc5NS05YzNhLTZiMTZhOGRmYjkxNw=="
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"  # Версия API
GIGACHAT_MODEL = "GigaChat"  # Явное указание модели
GIGACHAT_STREAMING = False  # Без потоковой передачи
VERIFY_SSL_CERTS = False  # Отключение проверки SSL-сертификатов
GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/models"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # Лог в файл
        logging.StreamHandler()  # Лог в консоль
    ]
)


async def start(update: Update, context):
    """Обработчик команды /start"""
    logging.info(f"Пользователь {update.message.chat.id} запустил бота")
    await update.message.reply_text("Привет! Я бот, который отвечает с помощью GigaChat.")


def ask_gigachat(prompt, user_id):
    """Функция отправки запроса в GigaChat с логированием"""
    headers = {
        "Authorization": f"Bearer {GIGACHAT_CREDENTIALS}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GIGACHAT_MODEL,
        "scope": GIGACHAT_SCOPE,
        "streaming": GIGACHAT_STREAMING,
        "verify_ssl_certs": VERIFY_SSL_CERTS,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    logging.info(f"[GigaChat Request] User {user_id}: {prompt}")

    try:
        response = requests.post(GIGACHAT_API_URL, json=data, headers=headers, verify=VERIFY_SSL_CERTS)

        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("choices", [{}])[0].get("message", {}).get("content",
                                                                                         "Ошибка в ответе GigaChat")
            logging.info(f"[GigaChat Response] User {user_id}: {response_text}")
            return response_text
        else:
            logging.error(f"[GigaChat Error] {response.status_code}: {response.text}")
            return f"Ошибка: {response.status_code}, {response.text}"

    except Exception as e:
        logging.exception(f"[GigaChat Exception] {e}")
        return "Произошла ошибка при запросе к GigaChat."


async def handle_message(update: Update, context):
    """Обработчик входящих сообщений"""
    user_text = update.message.text
    user_id = update.message.chat.id
    response = ask_gigachat(user_text, user_id)
    await update.message.reply_text(response)


# Создание и запуск бота
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logging.info("Бот запущен...")
app.run_polling()
