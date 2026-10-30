from html import escape

from bot.keyboards.public.content_actions import content_actions_keyboard
from bot.keyboards.public.main_menu import mainMenuKeyboard
from bot.keyboards.public.library_menu import libraryMenuKeyboard
from bot.keyboards.public.poem_category_menu import build_category_keyboard
from bot.keyboards.public.share_work_menu import share_work_keyboard
from bot.keyboards.share_work_categories import share_work_categories

from database.public.cotents import (
    fetch_by_category,
    create_content
)

from database.public.favourite import (
    delete_favourite,
    is_favourite,
    create_favourite,
    fetch_favourite,
    fetch_all_favourites
)

from database.public.users import is_user_banned
LITERATURE_TYPES = {
    "poems": ("poem", "ግጥሞች", "Poems"),
    "reflections": ("reflection", "ነጸብራቆች", "Reflections"),
    "lyrics": ("lyrics", "የዘፈን ግጥሞች", "Lyrics"),
    "short_story": ("short_story", "አጫጭር ታሪኮች", "Short Stories"),
}

CATEGORY_NAMES = {
    "nature": "Nature",
    "philosophy": "Philosophy",
    "love": "Love",
    "life_lesson": "Life Lessons",
}


def menu_handler(bot):

    @bot.callback_query_handler(
        func=lambda call: call.data == "library"
    )
    
    def library_callback(call):
        bot.answer_callback_query(call.id)
        user_id=call.from_user.id
        if is_user_banned(user_id):
                bot.send_message(
                    call.message.chat.id,
                    "🚫 You are banned from using this bot."
                )
                return
        bot.send_message(
            call.message.chat.id,
            "📚 ወደ ሥነ ጽሑፍ ቤተ መዛግብት በደህና መጡ!\n\n"
            "📚 Welcome to the Literature Archive!\n\n"
            "የሚፈልጉትን የሥነ ጽሑፍ ዓይነት ይምረጡ።\n"
            "Choose a literature type:",
            reply_markup=libraryMenuKeyboard
        )

    # Open the selected literature type's category menu
    @bot.callback_query_handler(
        func=lambda call: call.data in LITERATURE_TYPES
    )
    def literature_type_callback(call):
        bot.answer_callback_query(call.id)
        user_id=call.from_user.id
        content_type, amharic_name, english_name = (
            LITERATURE_TYPES[call.data]
        )
        if is_user_banned(user_id):
            bot.send_message(
                    call.message.chat.id,
                     "🚫 You are banned from using this bot."
                     )
            return
        bot.send_message(
            call.message.chat.id,
            f"📚 {amharic_name}\n"
            f"📚 {english_name}\n\n"
            "የሚፈልጉትን ምድብ ይምረጡ።\n"
            "Choose a category:",
            reply_markup=build_category_keyboard(content_type)
        )

    # Fetch and display matching literature
    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("category:")
    )
    def category_callback(call):
        bot.answer_callback_query(call.id)
        user_id=call.from_user.id
        if is_user_banned(user_id):
            bot.send_message(
                            call.message.chat.id,
                             "🚫 You are banned from using this bot."
                             )
            return
        try:
            _, content_type, category = call.data.split(":", 2)

            if content_type not in {
                item[0] for item in LITERATURE_TYPES.values()
            }:
                return

            if category not in CATEGORY_NAMES:
                return

        except ValueError:
            return

        data = fetch_by_category(category, content_type)
        chat_id = call.message.chat.id
        user_id=call.from_user.id

        if not data:
            bot.send_message(
                chat_id,
                f"No {CATEGORY_NAMES[category].lower()} "
                f"{content_type.replace('_', ' ')} available yet."
            )
            return
        for content_id,title, body,content_type, author_name, source, category,status,is_published in data:
            is_it_favourited=bool(is_favourite(content_id,user_id))

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

            )

            bot.send_message(
                chat_id,
                message_text,
                parse_mode="HTML",
                reply_markup=content_actions_keyboard(content_id,is_it_favourited)
            )

    @bot.callback_query_handler(
    func=lambda call: call.data.startswith("remove_favourite:")
    )
    def remove_favourite_callback(call):
        user_id=call.from_user.id
        if is_user_banned(user_id):
            bot.send_message(
                            call.message.chat.id,
                             "🚫 You are banned from using this bot."
                             )
            return
        content_id = int(call.data.split(":", 1)[1])
        user_id = call.from_user.id

        delete_favourite(content_id, user_id)

        bot.answer_callback_query(call.id, "Removed from Favorites!")

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=content_actions_keyboard(content_id, False)
        )


    @bot.callback_query_handler(
    func=lambda call: call.data.startswith("add_favourite:")
    )
    def add_favourite_callback(call):
        user_id=call.from_user.id
        if is_user_banned(user_id):
            bot.send_message(
                            call.message.chat.id,
                             "🚫 You are banned from using this bot."
                             )
            return
        content_id = int(call.data.split(":", 1)[1])
        user_id = call.from_user.id

        create_favourite(user_id, content_id)

        bot.answer_callback_query(call.id, "Added to Favorites!")

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=content_actions_keyboard(content_id, True)
        )
    @bot.callback_query_handler(func=lambda call: call.data.startswith("favourites"))
    def my_favourite(call):
        user_id=call.from_user.id
        if is_user_banned(user_id):
                    bot.send_message(
                                    call.message.chat.id,
                                     "🚫 You are banned from using this bot."
                                     )
                    return
        chat_id=call.message.chat.id
        content_type=call.data.split(":",1)[1]
        data=fetch_favourite(user_id,content_type)
        if not data:
                    bot.send_message(
                        chat_id,
                        f"No favourite "
                        f"{content_type.replace('_', ' ')} available yet."
                    )
                    return
        
        for content_id,content_type,title, body, author_name, category,source,saved_at,status,is_published in data:
                    is_it_favourited=bool(is_favourite(content_id,user_id))
        
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
        
                    )
        
                    bot.send_message(
                        chat_id,
                        message_text,
                        parse_mode="HTML",
                        reply_markup=content_actions_keyboard(content_id,is_it_favourited)
                    )
    @bot.callback_query_handler(func=lambda call: call.data=="all_favourites")
    def my_all_favourite(call):
                bot.answer_callback_query(call.id)
                user_id=call.from_user.id
                if is_user_banned(user_id):
                            bot.send_message(
                                            call.message.chat.id,
                                             "🚫 You are banned from using this bot."
                                             )
                            return
                chat_id=call.message.chat.id
                data=fetch_all_favourites(user_id)
                print(data)
                if not data:
                            bot.send_message(
                                chat_id,
                                f"no favourite available yet."
                            )
                            return
                
                for content_id,title,body,author_name,source,category,status,is_published, saved_at in data:
                            is_it_favourited=bool(is_favourite(content_id,user_id))
                
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
                
                            )
                
                            bot.send_message(
                                chat_id,
                                message_text,
                                parse_mode="HTML",
                                reply_markup=content_actions_keyboard(content_id,is_it_favourited)
                            )
    # User submissions placeholder
    @bot.callback_query_handler(
        func=lambda call: call.data == "share_work"
    )
    def share_callback(call):
             
        message="""
            ✍️ **ሥራዎን ያጋሩ | Share Your Work**

                እንኳን ወደ የሥነ ጽሑፍ ማጋሪያ ክፍላችን በደህና መጡ!

                የራስዎን የጽሑፍ ሥራ ከሌሎች ጋር ለማጋራት ከታች ያለውን የሥራ ዓይነት ይምረጡ። ሥራዎ ከተገመገመና ከጸደቀ በኋላ በየዘመን ፍሬዎች የሥነ ጽሑፍ ቤተ መዛግብት ውስጥ ሊታተም ይችላል።

                Welcome to our literature-sharing space!

                Share your original work with the YEZEMEN FREWOCH community. Please select the type of content you would like to submit below. Your submission will be reviewed before it can be published in our literature archive.

                🌿 **ፈጠራዎን ያጋሩ፤ ለሌሎችም መነሳሳት ይሁኑ!**
                *Share your creativity and inspire others!*
            """
        bot.answer_callback_query(
            call.id)
        user_id=call.from_user.id
        if is_user_banned(user_id):
                bot.send_message(
                                    call.message.chat.id,
                                         "🚫 You are banned from using this bot."
                                                     )
                return
        bot.send_message(call.message.chat.id,message,reply_markup=share_work_keyboard)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("submit_type:"))
    def share_my_works(call):
        bot.answer_callback_query(call.id)
        user_id=call.from_user.id
        if is_user_banned(user_id):
              bot.send_message(
                                    call.message.chat.id,
                                         "🚫 You are banned from using this bot."
                                                     )
              return
        content_type = call.data.split(":", 1)[1]

        msg = bot.send_message(
            call.message.chat.id,
            "Enter the title (ርዕስ አስገባ)"
        )

        bot.register_next_step_handler(msg, process_title, content_type)


    def process_title(msg, content_type):
        user_id=msg.from_user.id
        if is_user_banned(user_id):
              bot.send_message(
                   msg.chat.id,
                    "🚫 You are banned from using this bot."
                                                     )
              return
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
        user_id=msg.from_user.id
        if is_user_banned(user_id):
                      bot.send_message(
                           msg.chat.id,
                            "🚫 You are banned from using this bot."
                                                             )
                      return
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
        user_id=msg.from_user.id
        if is_user_banned(user_id):
                      bot.send_message(
                           msg.chat.id,
                            "🚫 You are banned from using this bot."
                                                             )
                      return
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
        user_id=msg.from_user.id
        if is_user_banned(user_id):
                      bot.send_message(
                           msg.chat.id,
                            "🚫 You are banned from using this bot."
                                                             )
                      return
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
        user_id=msg.from_user.id
        if is_user_banned(user_id):
                      bot.send_message(
                           msg.chat.id,
                            "🚫 You are banned from using this bot."
                                                             )
                      return
        category = (msg.text or "").strip()
        submitted_by = msg.from_user.id

        success,response=create_content(
            title,
            body,
            content_type,
            author_name,
            source,
            category,
            submitted_by
        )
        if success:   
            bot.send_message(
            msg.chat.id,
            f"{response} please wait until admins approve it",
            )
        if not success:
               bot.send_message(
                           msg.chat.id,
                           f"🚫 Sorry, there is a content with this title and body.",
                           )
            

    # About placeholder
    @bot.callback_query_handler(
        func=lambda call: call.data == "about_us"
    )
    def about_callback(call):
        user_id=call.from_user.id
        if is_user_banned(user_id):
                      bot.send_message(
                           call.message.chat.id,
                            "🚫 You are banned from using this bot."
                                                             )
                      return
        bot.answer_callback_query(call.id)
        about_text=f"""
        📚 **<b>ስለ የዘመን ፍረዎች — YEZEMEN FREWOCH**</b>

የዘመን ፍረዎች የቃላትን ኃይል፣ የፈጠራን ውበት እና ትርጉም ያለውን አገላለጽ ለማክበር የተመሠረተ የሥነ-ጽሑፍና የማኅበረሰብ መድረክ ነው።

<b>**ተልዕኳችን**</b>

የሥነ-ጽሑፍ ወዳዶች ሀሳብን የሚያነቃቁ፣ ስሜትን የሚገልጹ እና የጽሑፍን ውበት የሚጠብቁ ግጥሞችን፣ የሕይወት ምልከታዎችን እና ጥቅሶችን የሚያገኙበት ምቹና አቀባባይ መድረክ መፍጠር ነው።

በዚህ መድረክ ተጠቃሚዎች የተለያዩ የሥነ-ጽሑፍ ሥራዎችን ማንበብ፣ የሚወዷቸውን ሥራዎች ማስቀመጥ እና የራሳቸውን የፈጠራ ሥራዎች ለግምገማና ለሕትመት ማቅረብ ይችላሉ።

እያንዳንዱ ትርጉም ያለው ቃል ሰዎችን የማቀራረብ፣ ሀሳቦችን የማነሳሳት እና በልብ ውስጥ የማይረሳ አሻራ የማሳረፍ ኃይል እንዳለው እናምናለን።

<b>**🌟 ራዕያችን**</b>

ፈጠራ የሚበረታታበት፣ የጸሐፊዎች ሥራ የሚከበርበት እና ትርጉም ያላቸው ቃላት አንባቢዎቻቸውን የሚያገኙበት ደማቅና ንቁ የሥነ-ጽሑፍ ማኅበረሰብ መገንባት ነው።

**📖 የምናቀርባቸው አገልግሎቶች**

• 📖 የግጥሞች፣ የሕይወት ምልከታዎች እና የጥቅሶች ስብስብ።

• ✍️ የራስን የሥነ-ጽሑፍ ሥራዎች ለግምገማና ለሕትመት የማቅረብ ዕድል።

• ❤️ የሚወዷቸውን ሥራዎች በግል ስብስብ ውስጥ የማስቀመጥ አገልግሎት።

• 🤝 በፈጠራ፣ በመከባበር እና በትርጉም ያለው አገላለጽ ዙሪያ የተገነባ ማኅበረሰብ።

<i>**የዘመን ፍሬዎች — ቃላት ትርጉም የሚያገኙበት፣ ፈጠራም ቤት የሚያገኝበት መድረክ።**</i>\n\n

visit our channel: <a href="https://t.me/yezemenFrewoch">
    የዘመን ፍሬዎች</a>
owner: <a href="https://t.me/zarathustra0666">
    wegen geremew</a>
developed by: <a href="https://t.me/zarathustra0666">
    wegen geremew</a>
"""
        bot.send_message(
            call.message.chat.id,
            about_text,
            parse_mode="HTML"
        )
    @bot.callback_query_handler(func=lambda call: call.data.startswith("share_category"))
    def get_share_category(call):
         user_id=call.from_user.id
         if is_user_banned(user_id):
                               bot.send_message(
                                    call.message.chat.id,
                                     "🚫 You are banned from using this bot."
                                                                      )
                               return
         category=call.data.split(":",2)[2]
         return category
    # Return to the main menu
    @bot.callback_query_handler(
        func=lambda call: call.data == "main_menu"
    )
    def main_menu_callback(call):
        bot.answer_callback_query(call.id)
        user_id=call.from_user.id
        if is_user_banned(user_id):
          bot.send_message(
                                           call.message.chat.id,
                                            "🚫 You are banned from using this bot."
                                                                             )
          return
        bot.send_message(
            call.message.chat.id,
            "🏠 ዋናው ምናሌ\n"
            "🏠 Main Menu",
            reply_markup=mainMenuKeyboard
        )
