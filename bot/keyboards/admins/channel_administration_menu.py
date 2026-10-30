from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

sync_publish_content_button = InlineKeyboardButton(
    text="📤 Sync Published works",
    callback_data="sync_published_channel_content"
)

channel_statistics_button = InlineKeyboardButton(
    text="📊 Channel Statistics",
    callback_data="channel_statistics"
)

channel_status_button = InlineKeyboardButton(
    text="🔍 Channel Status",
    callback_data="channel_status"
)

back_to_admin_panel_button = InlineKeyboardButton(
    text="⬅️ Back to Admin Panel",
    callback_data="admin_main_menu"
)

channel_administration_keyboard = InlineKeyboardMarkup(row_width=2)

channel_administration_keyboard.add(
    sync_publish_content_button,
    channel_statistics_button,
    channel_status_button,
    back_to_admin_panel_button
)

