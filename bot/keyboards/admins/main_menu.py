from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

pendings_button=InlineKeyboardButton(text="📥pending submissions",callback_data="pending_submissions")
manage_contents_button=InlineKeyboardButton(text="📚 Content Management",callback_data="content_management")
manage_users_button=InlineKeyboardButton(text="👥 Manage Users",callback_data="manage_users")
channel_administration_button = InlineKeyboardButton(
    text="📢 Channel Administration",
    callback_data="channel_administration"
)

main_menu_keyboard=InlineKeyboardMarkup(row_width=2)
main_menu_keyboard.add(pendings_button,manage_contents_button,manage_users_button,channel_administration_button)



