
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


# Main Manage Published Works keyboard
view_published_works_button = InlineKeyboardButton(
    text="📚 View Published Works",
    callback_data="view_published_works"
)

search_published_works_button = InlineKeyboardButton(
    text="🔎 Search Works",
    callback_data="search_published_works"
)

published_works_keyboard = InlineKeyboardMarkup(row_width=2)
published_works_keyboard.add(
    view_published_works_button,
    search_published_works_button
)


# Display a list of published works
def published_works_list_keyboard(works):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for work in works:
        content_id, title = work[0], work[1]

        keyboard.add(
            InlineKeyboardButton(
                text=f"📖 {title[:45]} (ID: {content_id})",
                callback_data=f"published_work:{content_id}"
            )
        )

    return keyboard


# Actions for one selected work
def published_work_actions_keyboard(content_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="✏️ Edit Work",
            callback_data=f"edit_published_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="📤 Unpublish",
            callback_data=f"confirm_unpublish_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="🗑️ Delete Work",
            callback_data=f"confirm_delete_work:{content_id}"
        )
    )

    return keyboard


# Confirm unpublishing
def confirm_unpublish_keyboard(content_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="✅ Yes, Unpublish",
            callback_data=f"unpublish_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"published_work:{content_id}"
        )
    )

    return keyboard


# Confirm permanent deletion
def confirm_delete_keyboard(content_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="🗑️ Yes, Delete",
            callback_data=f"delete_published_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="❌ Cancel",
            callback_data=f"published_work:{content_id}"
        )
    )

    return keyboard

# Main dashboard: add this button to published_works_keyboard
manage_unpublished_works_button = InlineKeyboardButton(
    text="📥 Manage Unpublished Works",
    callback_data="manage_unpublished_works"
)

published_works_keyboard.add(manage_unpublished_works_button)


# Display unpublished works
def unpublished_works_list_keyboard(works):
    keyboard = InlineKeyboardMarkup(row_width=1)

    for content_id, title in works:
        keyboard.add(
            InlineKeyboardButton(
                text=f"📄 {title[:45]} (ID: {content_id})",
                callback_data=f"unpublished_work:{content_id}"
            )
        )

    return keyboard


# Actions for an unpublished work
def unpublished_work_actions_keyboard(content_id):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text="🔄 Republish",
            callback_data=f"republish_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="✏️ Edit Work",
            callback_data=f"edit_unpublished_work:{content_id}"
        ),
        InlineKeyboardButton(
            text="🗑️ Delete Work",
            callback_data=f"confirm_delete_unpublished:{content_id}"
        )
    )

    return keyboard

