from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_category_keyboard(content_type):
    keyboard = InlineKeyboardMarkup(row_width=2)

    categories = [
        ("🌿 ተፈጥሮ | Nature", "nature"),
        ("💭 ፍልስፍና | Philosophy", "philosophy"),
        ("❤️ ፍቅር | Love", "love"),
        ("🌱 የሕይወት ትምህርት | Life Lesson", "life_lesson"),
        ("❤️ የወደድኳቸው | My Favorites", "my_favourites"),
    ]
    for label, category in categories:
        if category == "my_favourites":
            callback_data = f"favourites:{content_type}"
        else:
            callback_data = f"category:{content_type}:{category}"

        keyboard.add(
            InlineKeyboardButton(
                text=label,
                callback_data=callback_data
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text="↩️ ወደ ቤተ መዛግብት | Back",
            callback_data="library"
        )
    )

    return keyboard
