from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def share_work_categories(content_type):
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    categories = ["love", "nature", "philosophy","life_lesson"]

    for category in categories:
        markup.add(KeyboardButton(category))

    return markup