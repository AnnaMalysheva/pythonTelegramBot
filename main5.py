from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import asyncio  # Библиотека для выполнения нескольких строчек кода одновременно
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from database import database as db
from bs4 import BeautifulSoup
import requests

from config import TOKEN
import time  # Время

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
target_time = [20, 3]  # Время, когда будет производиться рассылка
# Переменная для рассылки
first = True


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    calendar, step = DetailedTelegramCalendar().build()
    await bot.send_message(message.chat.id,
                           f"Select {LSTEP[step]}",
                           reply_markup=calendar)


@dp.callback_query_handler(DetailedTelegramCalendar.func())
async def inline_kb_answer_callback_handler(query):
    result, key, step = DetailedTelegramCalendar().process(query.data)

    if not result and key:
        await bot.edit_message_text(f"Select {LSTEP[step]}",
                                    query.message.chat.id,
                                    query.message.message_id,
                                    reply_markup=key)
    elif result:
        await db.insert_analytics(query.from_user.id, result)
        await bot.edit_message_text(f"You selected {result}",
                                    query.message.chat.id,
                                    query.message.message_id)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отправлю этот текст тебе в ответ!")


@dp.message_handler()
async def echo_message(msg: types.Message):
    if msg.text == "Привет":
        # Готовим кнопки
        keyboard = types.InlineKeyboardMarkup()
        key_pollution = types.InlineKeyboardButton(text='Получить данные', callback_data='get_data')
        keyboard.add(key_pollution)
        key_send_data = types.InlineKeyboardButton(text='Отправить данные', callback_data='send_data')
        keyboard.add(key_send_data)
        await bot.send_message(msg.from_user.id, text="Выбери что ты хочешь делать.", reply_markup=keyboard)
    else:
        await bot.send_message(msg.from_user.id, "Я тебя не понимаю. Напиши что-то другое.")


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


async def save_data_meteonova():
    news_url = "https://www.meteonova.ru/allergy/27553-Nizhniy_Novgorod.htm"
    r = requests.get(news_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.text, features="html.parser")
    allergy_div = soup.find("div", {"id": "frc_content_weather"})
    forecast = allergy_div.find_all("table")[0]

    for row in forecast.find_all('tr'):
        columns = row.find_all('td')
        if len(columns) > 0:
            await db.insert_all_analytics(columns[0].get_text(), columns[len(columns) - 1].get_text())


@dp.callback_query_handler(lambda c: c.data == 'get_data')
async def process_callback_button1(callback_query: types.CallbackQuery):
    data = await get_data_meteonova()
    resp = ''
    for k, v in data.items():
        resp += '<b>{}</b>, {}\n'.format(k, v)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, resp, parse_mode='HTML')


@dp.callback_query_handler(lambda c: c.data == 'send_data')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    calendar, step = DetailedTelegramCalendar().build()
    await bot.send_message(callback_query.from_user.id,
                           f"Select {LSTEP[step]}",
                           reply_markup=calendar)


# Рассылка
async def mailing():
    global first
    while True:
        now_time = [time.localtime()[3], time.localtime()[4]]
        if target_time == now_time:
            if first:
                first = False
                await save_data_meteonova()
        else:
            first = True
            await bot.get_me()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(mailing())
    executor.start_polling(dp)
