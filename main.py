import telebot
import config
import requests
from telebot import types
from bs4 import BeautifulSoup
import logging
import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

from telebot.types import ReplyKeyboardRemove, CallbackQuery

bot = telebot.TeleBot(config.TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
# Creates a unique calendar
calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


def get_data_gismeteo():
    news_url = "https://www.gismeteo.ru/weather-nizhny-novgorod-4355/"
    r = requests.get(news_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'})

    soup = BeautifulSoup(r.text, features="html.parser")
    allergy_div = soup.find("div", {"data-widget-id": "allergy"})
    forecast = allergy_div.find_all("div", {'class': 'widget__item'})

    attributes = dict()

    for item in forecast:
        if not f"day_{item.attrs['data-item']}" in attributes:
            attributes[f"day_{item.attrs['data-item']}"] = dict()
        date = item.find_all('div', {'class': 'w_time'})
        value = item.find_all('div', {'class': 'widget__value'})
        if date:
            text_day = item.text.replace('\n', ' ')
            attributes[f"day_{item.attrs['data-item']}"]['time'] = ' '.join(text_day.split())
        if value:
            text_value = item.text.replace('\n', '')
            attributes[f"day_{item.attrs['data-item']}"]['value'] = int(''.join(text_value.split()))
    return attributes

def get_data_meteonova():
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


@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    if message.text == "Привет":
        # Готовим кнопки
        keyboard = types.InlineKeyboardMarkup()
        key_pollution = types.InlineKeyboardButton(text='Получить данные', callback_data='get_data')
        keyboard.add(key_pollution)
        key_send_data = types.InlineKeyboardButton(text='Отправить данные', callback_data='send_data')
        keyboard.add(key_send_data)
        bot.send_message(message.from_user.id, text="Выбери что ты хочешь делать.", reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши что-то другое.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "get_data":
        data = get_data_meteonova()
        resp = ''
        for k, v in data.items():
            resp += '<b>{}</b>, {}\n'.format(k, v)
        bot.send_message(call.message.chat.id, resp, parse_mode='HTML')
    if call.data == "send_data":
        now = datetime.datetime.now()  # Get the current date
        bot.send_message(call.message.chat.id, "Selected date", reply_markup=calendar.create_calendar(
                name=calendar_1_callback.prefix,
                year=now.year,
                month=now.month,  # Specify the NAME of your calendar
            ),
        )
    if call.data.startswith(calendar_1_callback.prefix):
        # At this point, we are sure that this calendar is ours. So we cut the line by the separator of our calendar
        name, action, year, month, day = call.data.split(calendar_1_callback.sep)
        # Processing the calendar. Get either the date or None if the buttons are of a different type
        date = calendar.calendar_query_handler(
            bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
        )
        # There are additional steps. Let's say if the date DAY is selected, you can execute your code. I sent a message.
        if action == "DAY":
            bot.send_message(
                chat_id=call.from_user.id,
                text=f"You have chosen {date.strftime('%d.%m.%Y')}",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(f"{calendar_1_callback}: Day: {date.strftime('%d.%m.%Y')}")
        elif action == "CANCEL":
            bot.send_message(
                chat_id=call.from_user.id,
                text="Cancellation",
                reply_markup=ReplyKeyboardRemove(),
            )
            print(f"{calendar_1_callback}: Cancellation")


bot.polling(none_stop=True, interval=0)
