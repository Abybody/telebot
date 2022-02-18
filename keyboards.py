from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup




# ниже кнопки
button_1 = KeyboardButton('👤Профиль')
button_2 = KeyboardButton('💰Баланс')
button_3 = KeyboardButton('📝Цены')
button_4 = KeyboardButton('👍🏻Поддержка')
button_5 = KeyboardButton('✅Войти в аккаунт')
button_7 = KeyboardButton('🔥Крутить')

# всплывающая кнопка
inline_btn_1 = InlineKeyboardButton('Реферальная система', callback_data='button6')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


mainMenu = ReplyKeyboardMarkup(resize_keyboard = True).add(button_1, button_2, button_3, button_4, button_5, button_7)
