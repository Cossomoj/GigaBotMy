import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Твой API-токен от BotFather
TELEGRAM_BOT_TOKEN = "7302486009:AAEjvjmgyeqFU2Hd_KgL5SgHmwAtKL0O1Q0"

# Настройки GigaChat API
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Твои учетные данные для Basic Auth (нужно заменить)
GIGACHAT_AUTH_KEY = "NzU0ZjA2NzctYjlmOC00M2UxLWExNWQtNmQwNTIxMjg1Yzc3OjBiMjY2ZTIwLWI5YzQtNDc5NS05YzNhLTZiMTZhOGRmYjkxNw=="  # В формате 'Basic <base64-кодированные креды>'
VERIFY_SSL_CERTS = False  # Отключение проверки SSL-сертификатов

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),  # Лог в файл
        logging.StreamHandler()  # Лог в консоль
    ]
)


def get_gigachat_token():
    """Получает новый Access Token для GigaChat."""
    headers = {
        "Authorization": GIGACHAT_AUTH_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"scope": GIGACHAT_SCOPE}

    try:
        response = requests.post(GIGACHAT_AUTH_URL, headers=headers, data=data, verify=VERIFY_SSL_CERTS)
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logging.info("[GigaChat] Получен новый токен")
        return access_token
    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] Ошибка получения токена: {e}")
        return None


async def ask_gigachat(prompt, user_id):
    """Отправляет запрос в GigaChat-Max."""
    access_token = get_gigachat_token()
    if not access_token:
        return "Ошибка: не удалось получить токен GigaChat."

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "GigaChat-Max",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    logging.info(f"[GigaChat Request] User {user_id}: {prompt}")

    try:
        response = requests.post(GIGACHAT_CHAT_URL, json=data, headers=headers, verify=VERIFY_SSL_CERTS)
        response.raise_for_status()
        response_data = response.json()
        response_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Ошибка в ответе GigaChat")
        logging.info(f"[GigaChat Response] User {user_id}: {response_text}")
        return response_text
    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] {e}")
        return "Ошибка при запросе к GigaChat."


async def start(update: Update, context):
    """Обработчик команды /start"""
    logging.info(f"Пользователь {update.message.chat.id} запустил бота")
    await update.message.reply_text("Привет! Я бот, который отвечает с помощью GigaChat-Max.")


async def handle_message(update: Update, context):
    """Обработчик входящих сообщений"""
    user_text = update.message.text
    user_id = update.message.chat.id
    response = await ask_gigachat(user_text, user_id)
    await update.message.reply_text(response)


# Создание и запуск бота
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logging.info("Бот запущен...")
app.run_polling()