import config  # В нем находится токен
import logging  # Библиотека для логов
import asyncio  # Библиотека для выполнения нескольких строчек кода одновременно
import time  # Время
import datetime
from bs4 import BeautifulSoup
import requests
from aiogram import *  # Новая библиотека для работы с Telegram
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize

mailing_subs = []

# НАСТРОЙКИ РАССЫЛКИ
target_time = [22, 45]  # Время, когда будет производиться рассылка
mailing_text = '''Это текст рассылки'''  # Тест рассылки

# Подключение логов и бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dispatcher = Dispatcher(bot)

# Переменная для рассылки
first = True

# Creates a unique calendar
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


# Сам фунционал бота

@dispatcher.message_handler(commands=['subscribe'])
async def subscribe(message):
    if message.chat.id not in mailing_subs:
        mailing_subs.append(message.chat.id)
        await message.answer("Вы успешно подписались")
    else:
        await message.answer("Вы уже подписаны")


@dispatcher.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if message.chat.id in mailing_subs:
        mailing_subs.remove(message.chat.id)
    else:
        await message.answer("Вы уже подписаны")


async def get_data_meteonova():
    news_url = "https://www.meteonova.ru/allergy/27553-Nizhniy_Novgorod.htm"
    r = requests.get(news_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.text, features="html.parser")
    allergy_div = soup.find("div", {"id": "frc_content_weather"})
    forecast = allergy_div.find_all("table")[0]

    attributes = dict()

    for row in forecast.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) > 0:
            attributes[columns[0].get_text()] = columns[len(columns) - 1].get_text()
    return attributes


@dispatcher.message_handler(commands='start')
async def handle_text_messages(message):
    # Готовим кнопки
    keyboard = InlineKeyboardMarkup()
    key_pollution = InlineKeyboardButton(f"{emojize(':herb:')} {'Получить данные'}", callback_data='get_data')
    keyboard.add(key_pollution)
    key_send_data = InlineKeyboardButton(f"{emojize(':pencil:')} {'Отправить данные'}", callback_data='send_data')
    keyboard.add(key_send_data)
    await bot.send_message(message.from_user.id, text="Выбери что ты хочешь делать.", reply_markup=keyboard)


@dispatcher.callback_query_handler(lambda c: c.data == 'get_data')
async def callback_worker(callback_query: types.CallbackQuery):
    data = await get_data_meteonova()
    resp = ''
    for k, v in data.items():
        resp += '<b>{}</b>, {}\n'.format(k, v)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, resp, parse_mode='HTML')


# @dispatcher.callback_query_handler(func=lambda c: c.data == 'send_data')
#     if call.data == "send_data":
#         now = datetime.datetime.now()  # Get the current date
#         await bot.send_message(call.message.chat.id, "Selected date", reply_markup=calendar.create_calendar(
#             name=calendar_1_callback.prefix,
#             year=now.year,
#             month=now.month,  # Specify the NAME of your calendar
#         )

# @dispatcher.callback_query_handler(lambda c: c.data.startswith(calendar_1_callback.prefix))                              )
#         # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
#         name, action, year, month, day = call.data.split(calendar_1_callback.sep)
#         # Processing the calendar. Get either the date or None if the buttons are of a different type
#         date = calendar.calendar_query_handler(
#             bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
#         )
#         # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
#         if action == "DAY":
#             await bot.send_message(
#                 chat_id=call.from_user.id,
#                 text=f"You have chosen {date.strftime('%d.%m.%Y')}",
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#             print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
#         elif action == "CANCEL":
#             await bot.send_message(
#                 chat_id=call.from_user.id,
#                 text="Cancellation",
#                 reply_markup=ReplyKeyboardRemove(),
#             )
#             print(f"{calendar_1_callback}: Cancellation")


# Рассылка
async def mailing():
    global first
    while True:
        nowTime = [time.localtime()[3], time.localtime()[4]]
        if target_time == nowTime:
            if first:
                first = False
                if len(mailing_subs) == 0:
                    await bot.get_me()
                else:
                    for id in mailing_subs:
                        await bot.send_message(id, mailing_text)
        elif nowTime > target_time:
            first = True
            await bot.get_me()
        else:
            await bot.get_me()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(mailing())
    executor.start_polling(dispatcher, skip_updates=True)
