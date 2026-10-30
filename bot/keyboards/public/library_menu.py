from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton

poemsButton = InlineKeyboardButton(
    text="📝 ግጥሞች\n📖 Browse poems",
    callback_data='poems'
)

reflectionsButton = InlineKeyboardButton(
    text="🌿 ነጸብራቆች\n💭 Browse reflections",
    callback_data='reflections'
)

lyricsButton = InlineKeyboardButton(
    text="🎶 የዘፈን ግጥሞች\n🎵 Lyrics",
    callback_data='lyrics'
)

shortStoryButton = InlineKeyboardButton(
    text="📚 አጫጭር ታሪኮች\n✨ Short stories",
    callback_data='short_story'
)

mainMenuButton = InlineKeyboardButton(
    text="🏠 ዋናው መውጫ\n↩️ Main menu",
    callback_data='main_menu'
)
libraryMenuKeyboard=InlineKeyboardMarkup(row_width=2)
libraryMenuKeyboard.add(poemsButton,reflectionsButton,lyricsButton,shortStoryButton,mainMenuButton)