from html import escape
import hashlib
import os
from dotenv import load_dotenv
from config import CHANNEL_ID
from bot.keyboards.admins.channel_administration_menu import channel_administration_keyboard
from database.admins.channel_administration import fetch_publication,create_publication,fetch_pending_publications,update_publication
from database.admins.contents import fetch_contents_by_id
from database.admins.published_work import fetch_published_works_to_sync

from telebot.apihelper import ApiTelegramException

from database.admins.users import (
    fetch_specific_user_data,
    get_user_roles
)

from database.admins.channel import fetch_channel_statistics

load_dotenv()

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

from database.admins.users import (
    fetch_specific_user_data,
    get_user_roles,
)
def channel_administration_handler(bot):
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

    @bot.callback_query_handler(func=lambda call: call.data=="channel_administration")         
    def channal_administration_menu(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                    return
        bot.send_message(call.message.chat.id,"📢 <b>Welcome to Channel Administration!</b>\n\nManage your channel posts and publishing activities here.",reply_markup=channel_administration_keyboard,parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call:call.data=="sync_published_channel_content")
    def sync_contents(call):
        bot.answer_callback_query(call.id)
        if not require_active_admin(call.from_user.id, call.message.chat.id):
                            return
        works = fetch_published_works_to_sync()
        not_synchronized_contents=[]
        synchronized_contents=[]
        synchronized_already=[]
        if not works:
                    bot.send_message(
                        call.message.chat.id,
                        "📭 There are no published works yet."
                    )
                    return
        else:
              for content_id, title,body,author_name,content_type,category in works:
                    is_published_to_channel=fetch_publication(content_id,CHANNEL_ID)
                    if is_published_to_channel:
                        synchronized_already.append(title)
                    else:
                          success,result=create_publication(content_id,CHANNEL_ID)
                          if success:
                                synchronized_contents.append(title)
                          else:
                                not_synchronized_contents.append(title)
                
              if synchronized_contents:
                bot.send_message(call.message.chat.id, "📝 Works added to synchronization queue.")
              if not_synchronized_contents:
                    bot.send_message(call.message.chat.id, f"❌ These contents couldn't be synchronized\n\n{not_synchronized_contents} \n\n due to{result}")
              if synchronized_already:
                    bot.send_message(call.message.chat.id, "☑️ Works already registered.")

              
                
        pending_contents = fetch_pending_publications(CHANNEL_ID)

        posted_contents = []
        error_posted_contents = []
        missing_contents = []

        for publication_id, content_id, channel_id, message_id, status, posted_at, last_synced_at, content_hash, last_error in pending_contents:

            try:
                content = fetch_contents_by_id(content_id)

                if not content:
                    missing_contents.append(f"Content ID: {content_id}")
                    continue

                content_id, title, body, author_name, source, category = content

                text = (
                    f"<b>📖 {escape(str(title or 'Untitled'))}</b>\n\n"
                    f"\n{escape(str(body or ''))}\n"
                    f"\n\n<b>Author:</b> {escape(str(author_name or 'N/A'))}\n"
                    f"<b>Category:</b> {escape(str(category or 'N/A'))}\n"
                    f"<b>Source:</b> {escape(str(source or 'N/A'))}\n"
                    f"\n📚 @yezemenFrewoch"
                )

                # Send the content to the Telegram channel
                sent_message = bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=text,
                    parse_mode="HTML"
                )

                returned_message_id = sent_message.message_id
                content_hashed = hashlib.sha256(
                    text.encode("utf-8")
                ).hexdigest()

                # Update the publication record
                update_response = update_publication(
                    publication_id,
                    returned_message_id,
                    "posted",
                    content_hashed,
                    None
                )

                if update_response:
                    posted_contents.append(title)
                else:
                    error_posted_contents.append(title)

            except Exception as error:
                error_posted_contents.append(title if content else f"Content ID: {content_id}")

                bot.send_message(call.message.id,f"Publication error for content {content_id}: {error}")

        # Send synchronization report
        if posted_contents:
            bot.send_message(
                call.message.chat.id,
                f"✅ Successfully posted:\n\n" +
                "\n".join(posted_contents)
            )

        if error_posted_contents:
            bot.send_message(
                call.message.chat.id,
                f"❌ Failed to publish:\n\n" +
                "\n".join(error_posted_contents)
            )

        if missing_contents:
            bot.send_message(
                call.message.chat.id,
                f"⚠️ Content records not found:\n\n" +
                "\n".join(missing_contents)
            )

        if not posted_contents and not error_posted_contents and not missing_contents:
            bot.send_message(
                call.message.chat.id,
                "☑️ Everything is already synchronized!"
            )
    @bot.callback_query_handler(
        func=lambda call: call.data == "channel_statistics"
    )
    def channel_statistics_callback(call):
        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        if not require_active_admin(call.from_user.id, chat_id):
            return

        if not CHANNEL_ID:
            bot.send_message(
                chat_id,
                "⚠️ Channel ID is not configured."
            )
            return

        try:
            stats = fetch_channel_statistics(CHANNEL_ID)

            message = (
                "<b>📊 Channel Statistics</b>\n\n"
                f"📦 Total tracked posts: <b>{stats['total']}</b>\n\n"
                f"✅ Published: <b>{stats['posted']}</b>\n"
                f"🕒 Pending: <b>{stats['pending']}</b>\n"
                f"❌ Failed: <b>{stats['failed']}</b>\n"
                f"🗑 Removed: <b>{stats['removed']}</b>\n\n"
                "<i>Statistics are based on the bot's publication records.</i>"
            )

            bot.send_message(
                chat_id,
                message,
                parse_mode="HTML"
            )

        except Exception as error:
            print(f"Channel statistics error: {error}")

            bot.send_message(
                chat_id,
                "❌ Could not retrieve channel statistics."
            )

    # ---------------------------------
    # CHANNEL STATUS
    # ---------------------------------

    @bot.callback_query_handler(
        func=lambda call: call.data == "channel_status"
    )
    def channel_status_callback(call):
        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        if not require_active_admin(call.from_user.id, chat_id):
            return

        if not CHANNEL_ID:
            bot.send_message(
                chat_id,
                "⚠️ Channel ID is not configured."
            )
            return

        try:
            channel = bot.get_chat(CHANNEL_ID)

            bot_info = bot.get_me()

            member = bot.get_chat_member(
                CHANNEL_ID,
                bot_info.id
            )

            is_admin = member.status in ("administrator", "creator")

            if is_admin:
                can_post = getattr(member, "can_post_messages", False)
                can_edit = getattr(member, "can_edit_messages", False)
                can_delete = getattr(member, "can_delete_messages", False)

                status_message = (
                    "<b>🔍 Channel Status</b>\n\n"
                    f"📢 Channel: <b>{escape(channel.title or 'N/A')}</b>\n"
                    "<b>Bot Access</b>\n"
                    "🟢 Bot is an administrator\n\n"
                    "<b>Permissions</b>\n"
                    f"{'✅' if can_post else '❌'} Post messages\n"
                    f"{'✅' if can_edit else '❌'} Edit messages\n"
                    f"{'✅' if can_delete else '❌'} Delete messages"
                )

            else:
                status_message = (
                    "<b>🔍 Channel Status</b>\n\n"
                    f"📢 Channel: <b>{escape(channel.title or 'N/A')}</b>\n"
                    "🔴 Bot is not an administrator.\n\n"
                    "Please promote the bot and grant the required permissions."
                )

            bot.send_message(
                chat_id,
                status_message,
                parse_mode="HTML"
            )

        except ApiTelegramException as error:
            print(f"Channel status error: {error}")

            bot.send_message(
                chat_id,
                "❌ Cannot access the channel.\n\n"
                "Check the channel ID and make sure the bot has been added."
            )

        except Exception as error:
            print(f"Unexpected channel status error: {error}")

            bot.send_message(
                chat_id,
                "❌ An unexpected error occurred while checking channel status."
            )
