
import os
from html import escape

from dotenv import load_dotenv

from bot.keyboards.admins.manage_published import (
    published_works_keyboard,
    published_works_list_keyboard,
    published_work_actions_keyboard,
    confirm_unpublish_keyboard,
    confirm_delete_keyboard,
)

from database.admins.published_work import (
    fetch_published_works,
    search_published_works,
    fetch_published_work,
    update_published_work,
    unpublish_work,
    delete_published_work,
)
from bot.keyboards.admins.manage_published import (
    unpublished_works_list_keyboard,
    unpublished_work_actions_keyboard,
)

from database.admins.published_work import (
    fetch_unpublished_works,
    fetch_unpublished_work,
    republish_work,
    delete_unpublished_work,
)
from database.admins.users import get_user_roles


load_dotenv()
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))


def published_works_handler(bot):

    # Check permissions
    def can_manage_content(user_id):
        if user_id == BOT_OWNER_ID:
            return True

        roles = get_user_roles(user_id)

        return any(
            role[0] in ("admin", "moderator")
            for role in roles
        )

    def deny_access(call):
        bot.answer_callback_query(
            call.id,
            "You are not authorized to manage published works.",
            show_alert=True
        )

    # Display a selected work
    def show_published_work(chat_id, content_id):
        work = fetch_published_work(content_id)

        if not work:
            bot.send_message(
                chat_id,
                "❌ Published work not found. It may have been unpublished."
            )
            return

        (
            content_id,
            title,
            body,
            content_type,
            author_name,
            source,
            category,
            published_at,
        ) = work

        text = (
            f"<b>📖 {escape(str(title or 'Untitled'))}</b>\n\n"
            f"<b>ID:</b> <code>{content_id}</code>\n"
            f"<b>Type:</b> {escape(str(content_type or 'N/A'))}\n"
            f"<b>Author:</b> {escape(str(author_name or 'N/A'))}\n"
            f"<b>Category:</b> {escape(str(category or 'N/A'))}\n"
            f"<b>Source:</b> {escape(str(source or 'N/A'))}\n"
            f"<b>Published:</b> {escape(str(published_at or 'N/A'))}\n\n"
            f"<b>Content:</b>\n{escape(str(body or ''))}"
        )

        bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            reply_markup=published_work_actions_keyboard(content_id)
        )

    # Open the Manage Published Works dashboard
    @bot.callback_query_handler(
        func=lambda call: call.data == "manage_published_works"
    )
    def manage_published_works_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        bot.send_message(
            call.message.chat.id,
            "📚 <b>Manage Published Works</b>\n\n"
            "Choose an action:",
            parse_mode="HTML",
            reply_markup=published_works_keyboard
        )

    # View published works
    @bot.callback_query_handler(
        func=lambda call: call.data == "view_published_works"
    )
    def view_published_works_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        works = fetch_published_works()

        if not works:
            bot.send_message(
                call.message.chat.id,
                "📭 There are no published works yet."
            )
            return

        bot.send_message(
            call.message.chat.id,
            "📚 <b>Published Works</b>\n"
            "Select a work to manage:",
            parse_mode="HTML",
            reply_markup=published_works_list_keyboard(works)
        )

    # Search published works
    @bot.callback_query_handler(
        func=lambda call: call.data == "search_published_works"
    )
    def search_published_works_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        msg = bot.send_message(
            call.message.chat.id,
            "🔎 Enter the title or author name to search:"
        )
        bot.register_next_step_handler(msg, process_search)

    def process_search(message):
        if not message.text or not message.text.strip():
            bot.send_message(
                message.chat.id,
                "❌ Please enter a title or author name."
            )
            return

        keyword = message.text.strip()
        works = search_published_works(keyword)

        if not works:
            bot.send_message(
                message.chat.id,
                "📭 No published works matched your search."
            )
            return

        bot.send_message(
            message.chat.id,
            f"🔎 <b>Search results for:</b> {escape(keyword)}\n"
            "Select a work:",
            parse_mode="HTML",
            reply_markup=published_works_list_keyboard(works)
        )

    # Open a selected work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("published_work:")
    )
    def published_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        show_published_work(call.message.chat.id, content_id)

    # Begin editing a work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("edit_published_work:")
    )
    def edit_published_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        work = fetch_published_work(content_id)

        if not work:
            bot.send_message(
                call.message.chat.id,
                "❌ Published work not found."
            )
            return

        msg = bot.send_message(
            call.message.chat.id,
            "✏️ Enter the new title for this work:"
        )
        bot.register_next_step_handler(
            msg,
            process_edit_title,
            content_id
        )

    def process_edit_title(message, content_id):
        if not message.text or not message.text.strip():
            bot.send_message(
                message.chat.id,
                "❌ The title cannot be empty. Please start editing again."
            )
            return

        new_title = message.text.strip()

        msg = bot.send_message(
            message.chat.id,
            "📝 Enter the new body/content:"
        )
        bot.register_next_step_handler(
            msg,
            process_edit_body,
            content_id,
            new_title
        )

    def process_edit_body(message, content_id, new_title):
        if not message.text or not message.text.strip():
            bot.send_message(
                message.chat.id,
                "❌ The content cannot be empty. Please start editing again."
            )
            return

        new_body = message.text.strip()

        success = update_published_work(
            content_id,
            new_title,
            new_body
        )

        if success:
            bot.send_message(
                message.chat.id,
                "✅ Published work updated successfully."
            )
            show_published_work(message.chat.id, content_id)
        else:
            bot.send_message(
                message.chat.id,
                "❌ Could not update the work. It may no longer be published."
            )

    # Ask for unpublishing confirmation
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("confirm_unpublish_work:")
    )
    def confirm_unpublish_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        work = fetch_published_work(content_id)

        if not work:
            bot.send_message(
                call.message.chat.id,
                "❌ Published work not found."
            )
            return

        bot.send_message(
            call.message.chat.id,
            f"📤 Unpublish <b>{escape(str(work[1]))}</b>?\n\n"
            "It will no longer appear in the published archive, "
            "but the record will remain in the database.",
            parse_mode="HTML",
            reply_markup=confirm_unpublish_keyboard(content_id)
        )

    # Unpublish the work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("unpublish_work:")
    )
    def unpublish_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        if unpublish_work(content_id):
            bot.send_message(
                call.message.chat.id,
                "✅ Work unpublished successfully."
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Could not unpublish the work. It may already be unpublished."
            )

    # Ask for permanent deletion confirmation
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("confirm_delete_work:")
    )
    def confirm_delete_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        work = fetch_published_work(content_id)

        if not work:
            bot.send_message(
                call.message.chat.id,
                "❌ Published work not found."
            )
            return

        bot.send_message(
            call.message.chat.id,
            f"⚠️ Permanently delete <b>{escape(str(work[1]))}</b>?\n\n"
            "This action cannot be undone.",
            parse_mode="HTML",
            reply_markup=confirm_delete_keyboard(content_id)
        )

    # Permanently delete the selected work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("delete_published_work:")
    )
    def delete_published_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        if delete_published_work(content_id):
            bot.send_message(
                call.message.chat.id,
                "🗑️ Published work permanently deleted."
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Could not delete the work. It may already be deleted or unpublished."
            )
    
    # List unpublished works
    @bot.callback_query_handler(
        func=lambda call: call.data == "manage_unpublished_works"
    )
    def manage_unpublished_works_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        works = fetch_unpublished_works()

        if not works:
            bot.send_message(
                call.message.chat.id,
                "📭 No unpublished works found."
            )
            return

        bot.send_message(
            call.message.chat.id,
            "📥 <b>Unpublished Works</b>\n"
            "Select a work to manage:",
            parse_mode="HTML",
            reply_markup=unpublished_works_list_keyboard(works)
        )

    # Open a selected unpublished work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("unpublished_work:")
    )
    def unpublished_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        work = fetch_unpublished_work(content_id)

        if not work:
            bot.send_message(
                call.message.chat.id,
                "❌ Unpublished work not found."
            )
            return

        _, title, body, content_type, author, source, category, published_at = work


        text = (
            f"📥 <b>{escape(str(title or 'Untitled'))}</b>\n\n"
            f"<b>ID:</b> <code>{content_id}</code>\n"
            f"<b>Type:</b> {escape(str(content_type or 'N/A'))}\n"
            f"<b>Author:</b> {escape(str(author or 'N/A'))}\n"
            f"<b>Category:</b> {escape(str(category or 'N/A'))}\n\n"
            f"<b>Content:</b>\n{escape(str(body or ''))}"
        )

        if len(text) > 4000:
            text = text[:3950] + "\n\n... Content shortened."

        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode="HTML",
            reply_markup=unpublished_work_actions_keyboard(content_id)
        )

    # Republish an unpublished work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("republish_work:")
    )
    def republish_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.answer_callback_query(call.id, "Invalid work ID.")
            return

        if republish_work(content_id):
            bot.answer_callback_query(call.id, "Work republished!")
            bot.send_message(
                call.message.chat.id,
                "✅ The work has been republished successfully."
            )
        else:
            bot.answer_callback_query(
                call.id,
                "Cannot republish this work. Check its status.",
                show_alert=True
            )

    # Confirm deletion of an unpublished work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("confirm_delete_unpublished:")
    )
    def confirm_delete_unpublished_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        work = fetch_unpublished_work(content_id)

        if not work:
            bot.send_message(
                call.message.chat.id,
                "❌ Unpublished work not found."
            )
            return

        from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton(
                "🗑️ Yes, Delete",
                callback_data=f"delete_unpublished_work:{content_id}"
            ),
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data=f"unpublished_work:{content_id}"
            )
        )

        bot.send_message(
            call.message.chat.id,
            f"⚠️ Permanently delete <b>{escape(str(work[1]))}</b>?",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    # Delete an unpublished work
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("delete_unpublished_work:")
    )
    def delete_unpublished_work_callback(call):
        if not can_manage_content(call.from_user.id):
            deny_access(call)
            return

        bot.answer_callback_query(call.id)

        try:
            content_id = int(call.data.split(":", 1)[1])
        except (ValueError, IndexError):
            bot.send_message(call.message.chat.id, "❌ Invalid work ID.")
            return

        if delete_unpublished_work(content_id):
            bot.send_message(
                call.message.chat.id,
                "🗑️ Unpublished work deleted permanently."
            )
        else:
            bot.send_message(
                call.message.chat.id,
                "❌ Could not delete the work."
            )

