from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup
get_specific_user_button=InlineKeyboardButton(text="🔎 Find User",callback_data="find_specific_users")
get_all_users_button=InlineKeyboardButton(text="📋 View Users",callback_data="all_users")
promote_user_button=InlineKeyboardButton(text="🛡️ promote user",callback_data="promote_user")
remove_promoted_user_button=InlineKeyboardButton(text="🔐 Remove Role",callback_data="remove_role")
get_banned_users_button=InlineKeyboardButton(text="🚫 Banned Users",callback_data="get_banned_users")
ban_user_button=InlineKeyboardButton(text="🚫 Ban User",callback_data="ban_user")
unban_user_button = InlineKeyboardButton(
    text="✅ Unban User",
    callback_data="unban_user"
)
mainMenuButton = InlineKeyboardButton(
    text="🏠 ዋናው መውጫ\n↩️ Main menu",
    callback_data='admin_main_menu'
)
user_management_keyboard=InlineKeyboardMarkup(row_width=2)
user_management_keyboard.add(get_specific_user_button,get_all_users_button,promote_user_button,remove_promoted_user_button,get_banned_users_button,ban_user_button,unban_user_button,mainMenuButton)


