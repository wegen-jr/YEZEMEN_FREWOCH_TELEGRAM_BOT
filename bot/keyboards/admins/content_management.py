from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


add_new_work_button = InlineKeyboardButton(
    text="➕ Add New Work",
    callback_data="add_new_work"
)

manage_published_works_button = InlineKeyboardButton(
    text="📚 Manage Published Works",
    callback_data="manage_published_works"
)

mainMenuButton = InlineKeyboardButton(
    text="🏠 ዋናው መውጫ\n↩️ Main menu",
    callback_data='admin_main_menu'
)
# Content Management Keyboard
content_management_keyboard = InlineKeyboardMarkup(row_width=2)

content_management_keyboard.add(
    add_new_work_button,
    manage_published_works_button,
    mainMenuButton
)

