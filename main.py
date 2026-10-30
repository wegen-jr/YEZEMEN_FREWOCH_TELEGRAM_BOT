import telebot
import os
from dotenv import load_dotenv
from config import API_TOKEN
from bot.handlers.public.start import register_handlers
from bot.handlers.public.menu import menu_handler
from bot.handlers.admins.panel import admin_panel
from bot.handlers.admins.submissions import submission_hundler
from bot.handlers.admins.user_management import user_handler
from bot.handlers.admins.content_management import content_handler
from bot.handlers.admins.pubished_works import published_works_handler
from bot.handlers.admins.channel_administration import channel_administration_handler
from database.admins.users import ensure_owner_admin
from database.db import initialize_db
bot=telebot.TeleBot(token=API_TOKEN)

initialize_db()
load_dotenv()

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))

if BOT_OWNER_ID == 0:
    raise ValueError("BOT_OWNER_ID is missing from environment variables.")

ensure_owner_admin(BOT_OWNER_ID)

register_handlers(bot)
menu_handler(bot)
admin_panel(bot)
submission_hundler(bot)
user_handler(bot)
content_handler(bot)
published_works_handler(bot)
channel_administration_handler(bot)

bot.infinity_polling()