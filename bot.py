import requests
import logging
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = "7302486009:AAEjvjmgyeqFU2Hd_KgL5SgHmwAtKL0O1Q0"

# GigaChat API
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth/token"
GIGACHAT_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Учетные данные для авторизации
CLIENT_ID = "754f0677-b9f8-43e1-a15d-6d0521285c77"
CLIENT_SECRET = "fe13bda3-7638-4a1e-a869-070df5561826"

# Отключение проверки SSL-сертификатов (только для тестирования)
VERIFY_SSL_CERTS = True

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_gigachat_token():
    """Получает новый Access Token для GigaChat."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID.strip(),
        "client_secret": CLIENT_SECRET.strip(),
        "scope": GIGACHAT_SCOPE.strip()
    })
    logging.info("[GigaChat] 🔄 Запрос на получение токена...")
    try:
        response = requests.post(GIGACHAT_AUTH_URL, headers=headers, data=data, verify=VERIFY_SSL_CERTS)
        logging.info(f"[GigaChat] 🔍 Ответ сервера: {response.text}")
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logging.info("[GigaChat] ✅ Токен успешно получен")
        return access_token
    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка получения токена: {e} | Ответ: {response.text}")
        return None

async def ask_gigachat(prompt, user_id):
    """Отправляет запрос в GigaChat и получает ответ."""
    logging.info(f"[GigaChat] 🔄 Запрос пользователя {user_id}: {prompt}")
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
    try:
        response = requests.post(GIGACHAT_CHAT_URL, json=data, headers=headers, verify=VERIFY_SSL_CERTS)
        logging.info(f"[GigaChat] 🔍 Ответ сервера: {response.text}")
        response.raise_for_status()
        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"]
        logging.info(f"[GigaChat] ✅ Ответ пользователю {user_id}: {response_text}")
        return response_text
    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка запроса к GigaChat: {e}")
        return "Ошибка при запросе к GigaChat."

async def start(update: Update, context):
    """Обработчик команды /start"""
    logging.info(f"✅ Пользователь {update.message.chat.id} запустил бота")
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

logging.info("🚀 Бот запущен...")
app.run_polling()