from database.admins.auth import check_role
from bot.keyboards.admins.main_menu import main_menu_keyboard

def admin_panel(bot):
    @bot.message_handler(commands=['admin'])
    def admin_handler(message):
        user_id=message.from_user.id
        first_name=message.from_user.first_name
        print(user_id)
        is_admin=check_role(user_id)
        if is_admin:
            bot.send_message(message.chat.id, f"welcomback,<b>{first_name}</b>\n\n",parse_mode="HTML",reply_markup=main_menu_keyboard)
        else:
            bot.send_message(message.chat.id, "you are not admin. why are u trying to access the admin page?😡")
