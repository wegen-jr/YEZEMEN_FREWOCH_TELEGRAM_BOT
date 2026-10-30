
import os
from html import escape
from dotenv import load_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.keyboards.admins.main_menu import main_menu_keyboard
from bot.keyboards.admins.user_management import user_management_keyboard

from database.admins.users import (
    fetch_specific_user_data,
    fetch_users_data,
    get_user_roles,
    assign_role,
    remove_role as remove_role_in_db,
    ban_user as ban_user_in_db,
    fetch_banned_users,
    unban_user as unban_user_in_db
)

load_dotenv()
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))


def user_handler(bot):

    def require_active_admin(user_id, chat_id):
        admin = fetch_specific_user_data(user_id)

        if not admin:
            bot.send_message(
                chat_id,
                "❌ You are not registered with the bot."
            )
            return False

        if admin[4]:
            bot.send_message(
                chat_id,
                "🚫 Your account is banned. You cannot perform this action."
            )
            return False

        roles = get_user_roles(user_id)

        if not roles:
            bot.send_message(
                chat_id,
                "❌ You no longer have administrative privileges."
            )
            return False

        allowed_roles = ("admin", "moderator")

        if not any(role[0] in allowed_roles for role in roles):
            bot.send_message(
                chat_id,
                "❌ You no longer have administrative privileges."
            )
            return False

        return True

    # Get a readable role label for displaying users
    def get_role_label(user_id):
        roles = get_user_roles(user_id)

        if not roles:
            return "User"

        return ", ".join(str(role[0]) for role in roles)

    # User management dashboard
    @bot.callback_query_handler(
        func=lambda call: call.data == "manage_users"
    )
    def user_management(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        bot.send_message(
            call.message.chat.id,
            "Welcome to the user management dashboard\n",
            reply_markup=user_management_keyboard
        )

    # Find a specific user
    @bot.callback_query_handler(
        func=lambda call: call.data == "find_specific_users"
    )
    def get_specific_user(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        msg = bot.send_message(
            call.message.chat.id,
            "Enter user ID:"
        )
        bot.register_next_step_handler(msg, process_user_id)

    def process_user_id(message):
        chat_id = message.chat.id

        if not require_active_admin(message.from_user.id, chat_id):
            return

        user_id = message.text.strip()

        if not user_id.isdigit():
            bot.send_message(
                chat_id,
                "❌ Please enter a valid numeric user ID."
            )
            return

        data = fetch_specific_user_data(int(user_id))

        if not data:
            bot.send_message(chat_id, "❌ User not found.")
            return

        user_id, username, first_name, last_seen_at, is_banned = data
        role = get_role_label(user_id)

        rows = [
            f"{'ID':<12} {'USERNAME':<15} {'FIRST NAME':<15} "
            f"{'ROLE':<18} {'LAST SEEN':<15} {'BANNED?':<8}",
            "-" * 88
        ]

        rows.append(
            f"{user_id:<12} "
            f"{escape(str(username or 'N/A'))[:14]:<15} "
            f"{escape(str(first_name or 'N/A'))[:14]:<15} "
            f"{escape(role)[:17]:<18} "
            f"{str(last_seen_at or 'N/A')[:14]:<15} "
            f"{'Yes' if is_banned else 'No':<8}"
        )

        table = "\n".join(rows)

        bot.send_message(
            chat_id,
            f"<b>📋 Registered User</b>\n\n<pre>{table}</pre>",
            parse_mode="HTML"
        )

    # View all registered users
    @bot.callback_query_handler(
        func=lambda call: call.data == "all_users"
    )
    def get_all_users(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        chat_id = call.message.chat.id
        data = fetch_users_data()

        if not data:
            bot.send_message(chat_id, "No registered users found.")
            return

        rows = [
            f"{'ID':<12} {'USERNAME':<15} {'FIRST NAME':<15} "
            f"{'ROLE':<18} {'LAST SEEN':<15} {'BANNED?':<8}",
            "-" * 88
        ]

        for user_id, username, first_name, created_at, last_seen_at, is_banned in data:
            role = get_role_label(user_id)

            rows.append(
                f"{user_id:<12} "
                f"{escape(str(username or 'N/A'))[:14]:<15} "
                f"{escape(str(first_name or 'N/A'))[:14]:<15} "
                f"{escape(role)[:17]:<18} "
                f"{str(last_seen_at or 'N/A')[:14]:<15} "
                f"{'Yes' if is_banned else 'No':<8}"
            )

        table = "\n".join(rows)

        bot.send_message(
            chat_id,
            f"<b>📋 Registered Users</b>\n\n<pre>{table}</pre>",
            parse_mode="HTML"
        )

    # Promote a user
    @bot.callback_query_handler(
        func=lambda call: call.data == "promote_user"
    )
    def promote_user(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        if call.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                call.message.chat.id,
                "❌ Only the bot owner can assign roles."
            )
            return

        msg = bot.send_message(
            call.message.chat.id,
            "🛡️ Enter the user's Telegram ID:"
        )
        bot.register_next_step_handler(msg, process_promote_user)

    def process_promote_user(message):
        chat_id = message.chat.id

        if not require_active_admin(message.from_user.id, chat_id):
            return

        if message.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                chat_id,
                "❌ Only the bot owner can assign roles."
            )
            return

        user_input = message.text.strip()

        if not user_input.isdigit():
            bot.send_message(
                chat_id,
                "❌ Please enter a valid numeric Telegram ID."
            )
            return

        user_id = int(user_input)
        user = fetch_specific_user_data(user_id)

        if not user:
            bot.send_message(
                chat_id,
                "❌ User not found. They must be registered with the bot first."
            )
            return

        user_id, username, first_name, last_seen_at, is_banned = user

        if is_banned:
            bot.send_message(chat_id, "❌ This user is banned.")
            return

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(
                "🛡️ Admin",
                callback_data=f"assign_role:admin:{user_id}"
            ),
            InlineKeyboardButton(
                "🧹 Moderator",
                callback_data=f"assign_role:moderator:{user_id}"
            )
        )

        bot.send_message(
            chat_id,
            f"Choose a role for {escape(str(first_name or user_id))}:",
            parse_mode="HTML",
            reply_markup=markup
        )

    # Assign the selected role
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("assign_role:")
    )
    def assign_role_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        if call.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                call.message.chat.id,
                "❌ Only the bot owner can assign roles."
            )
            return

        try:
            _, role, user_id = call.data.split(":")
            user_id = int(user_id)
        except (ValueError, AttributeError):
            bot.send_message(call.message.chat.id, "❌ Invalid request.")
            return

        if role not in ("admin", "moderator"):
            bot.send_message(call.message.chat.id, "❌ Invalid role.")
            return

        success = assign_role(
            user_id,
            role,
            call.from_user.id
        )

        if success:
            bot.send_message(
                call.message.chat.id,
                f"✅ Role <b>{role}</b> assigned to user "
                f"<code>{user_id}</code>.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Could not assign role. It may already exist."
            )

    # Remove a user's role
    @bot.callback_query_handler(
        func=lambda call: call.data == "remove_role"
    )
    def remove_role_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        if call.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                call.message.chat.id,
                "❌ Only the bot owner can remove roles."
            )
            return

        msg = bot.send_message(
            call.message.chat.id,
            "🔐 Enter the user's Telegram ID:"
        )
        bot.register_next_step_handler(msg, process_remove_role)

    def process_remove_role(message):
        chat_id = message.chat.id

        if not require_active_admin(message.from_user.id, chat_id):
            return

        if message.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                chat_id,
                "❌ Only the bot owner can remove roles."
            )
            return

        user_input = message.text.strip()

        if not user_input.isdigit():
            bot.send_message(
                chat_id,
                "❌ Please enter a valid numeric Telegram ID."
            )
            return

        user_id = int(user_input)
        user = fetch_specific_user_data(user_id)

        if not user:
            bot.send_message(chat_id, "❌ User not found.")
            return

        user_id, username, first_name, last_seen_at, is_banned = user

        roles = get_user_roles(user_id)

        if not roles:
            bot.send_message(
                chat_id,
                "ℹ️ This user has no assigned roles."
            )
            return

        markup = InlineKeyboardMarkup(row_width=2)

        for (role,) in roles:
            markup.add(
                InlineKeyboardButton(
                    f"Remove {role}",
                    callback_data=f"remove_role_confirm:{role}:{user_id}"
                )
            )

        bot.send_message(
            chat_id,
            f"Select the role to remove from "
            f"{escape(str(first_name or user_id))}:",
            parse_mode="HTML",
            reply_markup=markup
        )

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("remove_role_confirm:")
    )
    def remove_role_confirm_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        if call.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                call.message.chat.id,
                "❌ Only the bot owner can remove roles."
            )
            return

        try:
            _, role, user_id = call.data.split(":")
            user_id = int(user_id)
        except (ValueError, AttributeError):
            bot.send_message(call.message.chat.id, "❌ Invalid request.")
            return

        if role not in ("admin", "moderator"):
            bot.send_message(call.message.chat.id, "❌ Invalid role.")
            return

        success = remove_role_in_db(user_id, role)

        if success:
            bot.send_message(
                call.message.chat.id,
                f"✅ Role <b>{role}</b> removed from "
                f"user <code>{user_id}</code>.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ This user does not have that role."
            )

    # Display banned users
    @bot.callback_query_handler(
        func=lambda call: call.data == "get_banned_users"
    )
    def get_banned_users_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        users = fetch_banned_users()

        if not users:
            bot.send_message(
                call.message.chat.id,
                "✅ No banned users found."
            )
            return

        rows = [
            f"{'ID':<14} {'USERNAME':<16} {'NAME':<16}",
            "-" * 46
        ]

        for user_id, username, first_name in users:
            rows.append(
                f"{user_id:<14} "
                f"{escape(str(username or 'N/A'))[:15]:<16} "
                f"{escape(str(first_name or 'N/A'))[:15]:<16}"
            )

        table = "\n".join(rows)

        bot.send_message(
            call.message.chat.id,
            f"<b>🚫 Banned Users</b>\n\n<pre>{table}</pre>",
            parse_mode="HTML"
        )

    # Ban a user
    @bot.callback_query_handler(
        func=lambda call: call.data == "ban_user"
    )
    def ban_user_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        msg = bot.send_message(
            call.message.chat.id,
            "🚫 Enter the user's Telegram ID:"
        )
        bot.register_next_step_handler(msg, process_ban_user)

    def process_ban_user(message):
        chat_id = message.chat.id

        if not require_active_admin(message.from_user.id, chat_id):
            return

        user_input = message.text.strip()

        if not user_input.isdigit():
            bot.send_message(
                chat_id,
                "❌ Invalid Telegram ID. Please enter a numeric user ID."
            )
            return

        user_id = int(user_input)
        user = fetch_specific_user_data(user_id)

        if not user:
            bot.send_message(chat_id, "❌ User not found.")
            return

        user_id, username, first_name, last_seen_at, is_banned = user

        if user_id == BOT_OWNER_ID:
            bot.send_message(
                chat_id,
                "❌ You can't ban the owner. Little admin 😁😁."
            )
            return

        if is_banned:
            bot.send_message(
                chat_id,
                "ℹ️ This user is already banned."
            )
            return

        response = ban_user_in_db(user_id)

        if response:
            bot.send_message(
                chat_id,
                f"🚫 {escape(str(first_name or user_id))} "
                "has been banned from using the bot.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                chat_id,
                "❌ Failed to ban this user."
            )

    # Unban a user
    @bot.callback_query_handler(
        func=lambda call: call.data == "unban_user"
    )
    def unban_user_callback(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        if call.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                call.message.chat.id,
                "❌ Only the bot owner can unban users."
            )
            return

        msg = bot.send_message(
            call.message.chat.id,
            "✅ Enter the Telegram ID of the user to unban:"
        )
        bot.register_next_step_handler(msg, process_unban_user)

    def process_unban_user(message):
        chat_id = message.chat.id

        if not require_active_admin(message.from_user.id, chat_id):
            return

        if message.from_user.id != BOT_OWNER_ID:
            bot.send_message(
                chat_id,
                "❌ Only the bot owner can unban users."
            )
            return

        user_input = message.text.strip()

        if not user_input.isdigit():
            bot.send_message(
                chat_id,
                "❌ Invalid Telegram ID. Please enter a numeric user ID."
            )
            return

        user_id = int(user_input)
        user = fetch_specific_user_data(user_id)

        if not user:
            bot.send_message(
                chat_id,
                "❌ User not found. They must be registered with the bot first."
            )
            return

        user_id, username, first_name, last_seen_at, is_banned = user

        if not is_banned:
            bot.send_message(
                chat_id,
                "ℹ️ This user is not currently banned."
            )
            return

        if unban_user_in_db(user_id):
            bot.send_message(
                chat_id,
                f"✅ <b>{escape(str(first_name or user_id))}</b> "
                "has been unbanned and can use the bot again.",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                chat_id,
                "❌ Could not unban this user. Please try again."
            )

    @bot.callback_query_handler(
        func=lambda call: call.data == "admin_main_menu"
    )
    def admin_main_menu(call):
        bot.answer_callback_query(call.id)

        if not require_active_admin(call.from_user.id, call.message.chat.id):
            return

        bot.send_message(
            call.message.chat.id,
            "<b>Admin Panel</b> ",
            reply_markup=main_menu_keyboard,
            parse_mode="HTML"
        )
