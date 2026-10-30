
from bot.keyboards.admins.content_management import content_management_keyboard
from bot.keyboards.admins.share_work_menu import share_work_keyboard
from bot.keyboards.share_work_categories import share_work_categories
from database.admins.contents import create_content

from database.admins.users import (
    fetch_specific_user_data,
    get_user_roles,
)
def content_handler(bot):

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
    @bot.callback_query_handler(func=lambda call: call.data=="content_management")
    def content_management(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                            return
        bot.send_message(call.message.chat.id, "📚 <b>Content Management</b> \n \nManage the literature archive",reply_markup=content_management_keyboard,parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data=="add_new_work")
    def add_content(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                            return
        bot.send_message(call.message.chat.id, "📚 <b>Content Management</b> \n \n choose content type",reply_markup=share_work_keyboard,parse_mode="HTML")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("admin"))
    def add_new_work(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                            return
        content_type=call.data.split(":",2)[2]
        msg = bot.send_message(
            call.message.chat.id,
            "Enter the title (ርዕስ አስገባ)"
        )

        bot.register_next_step_handler(msg, process_title, content_type)


    def process_title(msg, content_type):
        title = (msg.text or "").strip()

        if not title:
            reply = bot.send_message(msg.chat.id, "Title cannot be empty. Please enter the title:")
            bot.register_next_step_handler(reply, process_title, content_type)
            return

        reply = bot.send_message(
            msg.chat.id,
            "Enter the body (የግጥሙን ዋና ክፍል አስገባ)"
        )
        bot.register_next_step_handler(reply, process_body, content_type, title)


    def process_body(msg, content_type, title):
        body = (msg.text or "").strip()

        if not body:
            reply = bot.send_message(msg.chat.id, "Body cannot be empty. Please enter the body:")
            bot.register_next_step_handler(reply, process_body, content_type, title)
            return

        reply = bot.send_message(
            msg.chat.id,
            "Enter the author name (የባለቤቱን ስም አስገባ)"
        )
        bot.register_next_step_handler(
            reply, process_author_name, content_type, title, body
        )


    def process_author_name(msg, content_type, title, body):
        author_name = (msg.text or "").strip()

        if not author_name:
            reply = bot.send_message(
                msg.chat.id,
                "Author name cannot be empty. Please enter the author's name:"
            )
            bot.register_next_step_handler(
                reply, process_author_name, content_type, title, body
            )
            return

        reply = bot.send_message(
            msg.chat.id,
            "Enter the source. If it is your own work, enter your name.\n"
            "(ምንጭ አስገባ፤ የራስህ/ሽ ከሆነ ስም አስገባ)"
        )
        bot.register_next_step_handler(
            reply, process_source, content_type, title, body, author_name
        )


    def process_source(msg, content_type, title, body, author_name):
        source = (msg.text or "").strip()

        reply = bot.send_message(
            msg.chat.id,
            "Choose the category (የሥራውን ምድብ አስገባ)",
            reply_markup=share_work_categories(content_type)
        )

        bot.register_next_step_handler(
            reply,
            process_category,
            content_type,
            title,
            body,
            author_name,
            source
        )

    def process_category(
        msg, content_type, title, body, author_name, source
    ):
        category = (msg.text or "").strip()
        submitted_by = msg.from_user.id

        response=create_content(
            title,
            body,
            content_type,
            author_name,
            source,
            category,
            submitted_by
        )
        bot.send_message(
            msg.chat.id,
            f"{response}",
            )


