from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

poem_button = InlineKeyboardButton(
    text="📝 ግጥም | Poem",
    callback_data="admin:submit_type:poem"
)

reflection_button = InlineKeyboardButton(
    text="🌿 ነጸብራቅ | Reflection",
    callback_data="admin:submit_type:reflection"
)


lyrics_button = InlineKeyboardButton(
    text="🎶 የዘፈን ግጥም | Lyrics",
    callback_data="admin:submit_type:lyrics"
)

short_story_button = InlineKeyboardButton(
    text="📖 አጭር ታሪክ | Short Story",
    callback_data="admin:submit_type:short_story"
)

back_button = InlineKeyboardButton(
    text=" ተመለስ |↩️ Back",
    callback_data="content_management"
)

share_work_keyboard = InlineKeyboardMarkup(row_width=2)
share_work_keyboard.add(
    poem_button,
    reflection_button,
    lyrics_button,
    short_story_button,
    back_button
)