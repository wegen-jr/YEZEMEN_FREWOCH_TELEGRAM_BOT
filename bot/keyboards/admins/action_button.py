from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def actions_keyboard(content_id, is_pending):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if is_pending:
        approve_button = InlineKeyboardButton(
            text="✅ Approve",
            callback_data=f"approve:{content_id}"
        )
        reject_button= InlineKeyboardButton(
            text="❌ Reject",
            callback_data=f"reject:{content_id}"
        )

    keyboard.add(approve_button,reject_button)
    return keyboard