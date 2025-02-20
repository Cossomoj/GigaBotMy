import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Токен Telegram-бота
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# GigaChat API
GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGACHAT_CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Учетные данные для авторизации
CLIENT_ID = "754f0677-b9f8-43e1-a15d-6d0521285c77"
CLIENT_SECRET = "fe13bda3-7638-4a1e-a869-070df5561826"

# Отключение проверки SSL-сертификатов (не рекомендуется в продакшене)
VERIFY_SSL_CERTS = False

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
    """Получает новый Access Token для GigaChat с логами всех шагов."""
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": GIGACHAT_SCOPE
    }

    logging.info("[GigaChat] 🔄 Запрос на получение токена отправляется...")

    try:
        response = requests.post(GIGACHAT_AUTH_URL, headers=headers, data=data, verify=VERIFY_SSL_CERTS)
        logging.info(f"[GigaChat] 🔍 HTTP Status Code: {response.status_code}")

        # Логируем полный ответ сервера
        logging.debug(f"[GigaChat] 📩 Ответ от сервера: {response.text}")

        if response.status_code == 200:
            access_token = response.json().get("access_token")
            logging.info("[GigaChat] ✅ Токен успешно получен")
            return access_token
        else:
            logging.error(f"[GigaChat Error] ❌ Ошибка получения токена: {response.status_code} {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка соединения: {e}")
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
        logging.info(f"[GigaChat] 🔍 HTTP Status Code: {response.status_code}")
        logging.debug(f"[GigaChat] 📩 Ответ от сервера: {response.text}")

        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "Ошибка в ответе GigaChat")
            logging.info(f"[GigaChat] ✅ Ответ пользователю {user_id}: {response_text}")
            return response_text
        else:
            logging.error(f"[GigaChat Error] ❌ Ошибка запроса к GigaChat: {response.status_code} {response.text}")
            return "Ошибка при запросе к GigaChat."

    except requests.exceptions.RequestException as e:
        logging.error(f"[GigaChat Error] ❌ Ошибка соединения: {e}")
        return "Ошибка при соединении с GigaChat."


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
