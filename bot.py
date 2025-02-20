import requests
import logging
import base64
import uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = "7302486009:AAEjvjmgyeqFU2Hd_KgL5SgHmwAtKL0O1Q0"

# GigaChat API
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth/token"
GIGACHAT_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

# Учетные данные для авторизации
CLIENT_ID = "754f0677-b9f8-43e1-a15d-6d0521285c77"
CLIENT_SECRET = "fe13bda3-7638-4a1e-a869-070df5561826"

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
    try:
        # Кодирование client_id:client_secret в base64
        auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}".encode('ascii')
        b64_auth = base64.b64encode(auth_string).decode('ascii')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {b64_auth}"
        }

        data = "scope=GIGACHAT_API_PERS"

        logging.info("[GigaChat] 🔄 Запрос на получение токена...")
        response = requests.post(
            GIGACHAT_AUTH_URL,
            headers=headers,
            data=data,
            verify=True
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
        logging.info("[GigaChat] ✅ Токен успешно получен")
        return access_token

    except Exception as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка получения токена: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logging.error(f"Ответ сервера: {e.response.text}")
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
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            GIGACHAT_CHAT_URL,
            json=data,
            headers=headers,
            verify=True
        )
        response.raise_for_status()
        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"]
        logging.info(f"[GigaChat] ✅ Ответ пользователю {user_id}")
        return response_text

    except Exception as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка запроса: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logging.error(f"Ответ сервера: {e.response.text}")
        return "Ошибка при обработке запроса"


# Остальной код без изменений
async def start(update: Update, context):
    """Обработчик команды /start"""
    logging.info(f"✅ Пользователь {update.message.chat.id} запустил бота")
    await update.message.reply_text("Привет! Я бот, который отвечает с помощью GigaChat.")


async def handle_message(update: Update, context):
    """Обработчик входящих сообщений"""
    user_text = update.message.text
    user_id = update.message.chat.id
    response = await ask_gigachat(user_text, user_id)
    await update.message.reply_text(response)


app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

logging.info("🚀 Бот запущен...")
app.run_polling()