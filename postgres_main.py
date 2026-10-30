
import os
import telebot
from flask import Flask, request, abort
from dotenv import load_dotenv

load_dotenv()

from config import API_TOKEN

from bot.handlers.public.start import register_handlers
from bot.handlers.public.menu import menu_handler
from bot.handlers.admins.panel import admin_panel
from bot.handlers.admins.submissions import submission_hundler
from bot.handlers.admins.user_management import user_handler
from bot.handlers.admins.content_management import content_handler
from bot.handlers.admins.pubished_works import published_works_handler
from bot.handlers.admins.channel_administration import (
    channel_administration_handler,
)

from database.admins.users import ensure_owner_admin
from database.postgres_db import initialize_postgres_db


BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not API_TOKEN:
    raise ValueError("API_TOKEN is missing.")

if BOT_OWNER_ID == 0:
    raise ValueError("BOT_OWNER_ID is missing.")

if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET is missing.")

if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is missing.")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Initialize PostgreSQL
initialize_postgres_db()
ensure_owner_admin(BOT_OWNER_ID)

# Register existing handlers
register_handlers(bot)
menu_handler(bot)
admin_panel(bot)
submission_hundler(bot)
user_handler(bot)
content_handler(bot)
published_works_handler(bot)
channel_administration_handler(bot)

# Register Telegram webhook
webhook_endpoint = (
    f"{WEBHOOK_URL.rstrip('/')}/{WEBHOOK_SECRET}"
)

webhook_registered = bot.set_webhook(
    url=webhook_endpoint,
    secret_token=WEBHOOK_SECRET
)

if not webhook_registered:
    raise RuntimeError("Failed to register Telegram webhook.")

print("Telegram webhook registered successfully.")

@app.route("/", methods=["GET"])
def home():
    return "YEZEMEN FREWOCH bot is running.", 200


@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def telegram_webhook():

    secret_header = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if secret_header != WEBHOOK_SECRET:
        abort(403)

    if not request.is_json:
        abort(400)

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict) or "update_id" not in payload:
        abort(400)

    update = telebot.types.Update.de_json(payload)

    print("Received Telegram update:", update.update_id)

    try:
        bot.process_new_updates([update])
        print("Telegram update processed successfully.")

    except Exception as error:
        print("Telegram update processing failed:", repr(error))
        raise

    return "OK", 200
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
