
from bot.keyboards.public.main_menu import mainMenuKeyboard

from database.public.users import (
    fetch_specific_user_data,
    create_or_update_user,
    is_user_banned
)

from datetime import datetime, timezone


def register_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start_command(message):

        salutation = f"""
🌿 ወደ የዘመን ፍሬዎች እንኳን በደህና መጡ! 📚

ሰላም {message.from_user.first_name}! ✨

ቃላት ሐሳብን ወደ ልብ የሚያደርሱበት፣ ግጥም ስሜትን የሚተርክበት፣ ጥበብም ትውልድን የሚያገናኝበት የሥነ ጽሑፍ ዓለም ይህ ነው። 🖋️

በዚህ የሥነ ጽሑፍ ማዕድ፦

📖 ውብ ግጥሞችንና አስተማሪ ሐሳቦችን ያንብቡ።

❤️ የሚወዷቸውን ጽሑፎች ለወደፊት ያስቀምጡ።

✍️ የራስዎን ጽሑፎች በማጋራት የጥበብ ክብራችን አካል ይሁኑ።

🌱 እያንዳንዱ ቃል ፍሬ አለው፤ እያንዳንዱ ሐሳብም የሚያብብበት ጊዜ አለው።

የዘመን ፍሬዎች — የቃላት፣ የሐሳብና የጥበብ ማዕድ። 🌿
"""

        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name

        last_seen = datetime.now(timezone.utc).isoformat()

        if is_user_banned(user_id):
            bot.send_message(
                message.chat.id,
                "🚫 You are banned from using this bot."
            )
            return

        if fetch_specific_user_data(user_id):

            bot.send_message(
                user_id,
                f"welcome back, {first_name}",
                parse_mode="Markdown",
                reply_markup=mainMenuKeyboard
            )

            create_or_update_user(
                user_id,
                username,
                first_name,
                last_seen
            )

        else:

            bot.send_message(
                user_id,
                salutation,
                reply_markup=mainMenuKeyboard
            )

            create_or_update_user(
                user_id,
                username,
                first_name,
                last_seen
            )
