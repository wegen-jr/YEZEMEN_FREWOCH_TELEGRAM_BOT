from html import escape
from datetime import datetime
from database.admins.contents import fetch_pendings,update_status
from bot.keyboards.admins.action_button import actions_keyboard
from database.admins.users import (
    fetch_specific_user_data,
    get_user_roles,
)
def submission_hundler(bot):

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
    @bot.callback_query_handler(func=lambda call: call.data=="pending_submissions")
    def pending_submissions(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                    return
        chat_id=call.message.chat.id
        data=fetch_pendings('pending')
        if not data:
                            bot.send_message(
                                chat_id,
                                f"No pending contents "
                            )
                            return
        for content_id,title,body,content_type, author_name, source ,category,status in data:
                            is_pending=bool(fetch_pendings("pending"))
                
                            title = escape(str(title or "Untitled"))
                            body = escape(str(body or ""))
                            author_name = escape(str(author_name or "Unknown"))
                            source = escape(str(source or "Unknown"))
                            db_category = escape(str(category or "Uncategorized"))
                
                            message_text = (
                                f"📜 <b>{title}</b>\n\n"
                                f"{body}\n\n"
                                f"✍️ <b>Author: {author_name}\n</b>"
                                f"📚 <b>Source: {source}\n</b>"
                                f"🏷️ <b>Category: {db_category}</b>"
                                f"🏷️ <b>Category: {content_type}</b>"

                            )
                
                            bot.send_message(
                                chat_id,
                                message_text,
                                parse_mode="HTML",
                                reply_markup=actions_keyboard(content_id,is_pending)
                            )
    @bot.callback_query_handler(func=lambda call: call.data.startswith("approve"))
    def approve_content(call):
            bot.answer_callback_query(call.id)
            if not require_active_admin(call.from_user.id, call.message.chat.id):
                                return
            status="approved"
            content_id=call.data.split(":",1)[1]
            approved_by=call.from_user.id
            is_published=True
            published_at=datetime.now()
            response=update_status(status,approved_by,is_published,published_at,content_id)
            if response:
                bot.send_message(call.message.chat.id, "✅status updated successfully",)
            else:
                bot.send_message(call.message.chat.id, "update not successful",)
    @bot.callback_query_handler(func=lambda call: call.data.startswith("reject"))
    def reject_content(call):
                bot.answer_callback_query(call.id)
                if not require_active_admin(call.from_user.id, call.message.chat.id):
                                    return
                status="rejected"
                content_id=call.data.split(":",1)[1]
                rejected_by=call.from_user.id
                is_published=False
                rejected_at=datetime.now()
                response=update_status(status,rejected_by,is_published,rejected_at,content_id)
                if response:
                    bot.send_message(call.message.chat.id, "✅status updated successfully",)
                else:
                    bot.send_message(call.message.chat.id, "update not successful",)
                    

