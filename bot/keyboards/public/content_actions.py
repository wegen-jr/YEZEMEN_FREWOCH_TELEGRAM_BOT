from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def content_actions_keyboard(content_id, is_favourite):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if is_favourite:
        favourite_button = InlineKeyboardButton(
            text="💔 Remove from Favorites",
            callback_data=f"remove_favourite:{content_id}"
        )
    else:
        favourite_button = InlineKeyboardButton(
            text="❤️ Add to Favorites",
            callback_data=f"add_favourite:{content_id}"
        )

    keyboard.add(favourite_button)
    return keyboard