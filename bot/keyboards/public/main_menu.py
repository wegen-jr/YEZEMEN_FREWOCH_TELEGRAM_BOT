from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup

literatureArchiveButton=InlineKeyboardButton(text='📚 ሥነ ጽሑፍ ቤተ መዛግብት',callback_data='library')
myFavouritesButton=InlineKeyboardButton(text='❤️ የወደድኳቸው',callback_data='all_favourites')
sharePoemButton=InlineKeyboardButton(text='✍️ ሥራዬን አጋራ',callback_data='share_work')
aboutButton=InlineKeyboardButton(text='ℹ️ ስለ ቦቱ',callback_data='about_us')

mainMenuKeyboard=InlineKeyboardMarkup(row_width=2)
mainMenuKeyboard.add(literatureArchiveButton,myFavouritesButton,sharePoemButton,aboutButton)



