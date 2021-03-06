import telebot
from telebot import types
import time
import random
import yfinance as yf
import requests

stocks_list = ['AAPL', 'GOOG', 'AMZN', 'SPCE', 'TSLA', 'KO', 'GME', 'YNDX']

clients = dict()

stocks = dict()

stocks['sample_ticker'] = {'current_price': 5, 'company_name': '123', 'info': {}}
stocks['sample_ticker_1'] = {'current_price': 5, 'company_name': '123', 'info': {}}


def register_client(client_id):
    global clients
    if client_id not in clients:
        clients[client_id] = {'stocks': {},
                              'registration_date': 0,
                              'history': [],
                              'account': 1000000
                              }
        resp = 'Теперь ты в игре, '
    else:
        resp = 'А чо ты на старт жмешь, мы тя уже зарегали, уважаемый '
    return resp


def register_stock(item):
    global stocks
    if item not in stocks:
        stocks[item] = {'current_price': random.randint(0, 400), 'company_name': '123', 'info': {}}


for item in stocks_list:
    register_stock(item)


def buy(client_id, ticker, quantity):
    global stocks, clients
    cost = stocks[ticker]['current_price'] * quantity
    if ticker not in clients[client_id]['stocks'].keys():
        clients[client_id]['stocks'][ticker] = {'buy_price': 0, 'quantity': 0}
    clients[client_id]['account'] -= cost
    clients[client_id]['stocks'][ticker]['quantity'] += quantity
    clients[client_id]['stocks'][ticker]['buy_price'] = (quantity*stocks[ticker]['current_price'] + clients[client_id]['stocks'][ticker]['buy_price'] * clients[client_id]['stocks'][ticker]['quantity'])
    clients[client_id]['stocks'][ticker]['buy_price'] /=  quantity + clients[client_id]['stocks'][ticker]['quantity']
    clients[client_id]['stocks'][ticker]['buy_price'] = stocks[ticker]['current_price']


def sell(client_id, ticker, quantity):
    global stocks, clients                                               #возможно while
    cost = stocks[ticker]['current_price'] * quantity
    if ticker not in clients[client_id]['stocks'].keys():
        clients[client_id]['stocks'][ticker] = {'buy_price': stocks[ticker]['current_price'], 'quantity': 0}
    if quantity < clients[client_id]['stocks'][ticker]['quantity']:
        clients[client_id]['stocks'][ticker]['buy_price'] = stocks[ticker]['current_price']
    clients[client_id]['account'] += cost
    clients[client_id]['stocks'][ticker]['quantity'] -= quantity


def stocks_to_string(client_id, message):
    global stocks, total_cost
    total_cost = 0
    bot.send_message(message.chat.id, text='*Ваш портфель*', parse_mode='Markdown')
    for item in sorted(clients[client_id]['stocks'].keys()):
        s = stock_to_string(client_id, item, message)
        bot.send_message(message.chat.id, text=s, parse_mode='Markdown')

    total_cost += clients[client_id]['account']
    s = 'Валюта: ' + '{:>10.2f}'.format(clients[client_id]['account'])
    bot.send_message(message.chat.id, text=s, parse_mode='Markdown')
    s = 'Стомость всех активов: ' + '{:>10.2f}'.format(total_cost)
    bot.send_message(message.chat.id, text=s, parse_mode='Markdown')


def stock_to_string(client_id, item, message):
    global clients, stocks, total_cost
    q = '{:>20}'.format(clients[client_id]['stocks'][item]['quantity'])
    buy_p = '{:>12}'.format(clients[client_id]['stocks'][item]['buy_price'])
    cur_p = '{:>11.2f}'.format(stocks[item]['current_price'])
    cost = '{:>16.2f}'.format(float(cur_p) * float(q))
    total_cost += float(cost)
    change = round(float(cur_p)*100/float(buy_p),2)-100
    total_change=round(total_cost*change/100,2)

    s = '*' + item + '*' + '\n'
    s += 'Количество: ' + q + '\n'
    s += 'Цена покупки: ' + buy_p + '\n'
    s += 'Текущая цена: ' + cur_p + '\n'
    s += 'Стоимость: ' + cost + '\n'
    s += 'Изменение с момента сделки: ' + str(change) + ' %' + '\n'
    s += 'Изменение с момента сделки: ' + str(total_change) + ' bucks' + '\n'




    return s


def get_quantity(msg):
    global quantity
    quantity = int(msg.text)
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(types.KeyboardButton('Назад'), types.KeyboardButton('Подтвердить'))
    msg = bot.send_message(msg.chat.id, text='Подтвердите операцию', reply_markup=keyboard)
    bot.register_next_step_handler(msg, get_confirm)


def get_confirm(msg):
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(types.KeyboardButton('В главное меню'))
    if msg.text == 'Подтвердить':

        global quantity, ticker, operation

        if operation == 'BUY':
            buy(msg.from_user.id, ticker, quantity)
        elif operation == 'SELL':
            sell(msg.from_user.id, ticker, quantity)

        msg = bot.send_message(msg.chat.id, 'Операция успешно совершена!')
        bot.register_next_step_handler(msg, send_keyboard)


def get_price(symbol):
    data = yf.download(tickers=symbol, period='10m', interval='1m')
    return float(data['Close'][-1])


def pricechanger(ticker):
    global stocks
    price = round(get_price(ticker), 2)
    stocks[ticker]['current_price'] = price
    return price


import telebot
from telebot import types
import sqlite3
import random

import numpy as np
import pandas as pd
import psutil
from IPython.display import Image

# Data Source
import yfinance as yf

# Data viz
import plotly.graph_objs as go

import kaleido
import json
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.graph_objects as go
import collections

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def candles(data, type2=False):
    # declare figure
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'], name='market data'))

    # Add titles
    """fig.update_layout(
        #title='Uber live share price evolution',
        yaxis_title='Курс акций в долларах')
"""
    # Делаем кнопки для навигации
    """ fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                #dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1month", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    ) """

    # настраиваем размер графика
    fig.update_layout(autosize=True,
                      width=1000,
                      height=700, )

    # убираем разрывы меежду данными. Чтобы график был сплошной. То есть убираем выходные и часы, когда торговля не идет
    if type2:
        fig.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[
                # NOTE: Below values are bound (not single values), ie. hide x to y
                dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                # dict(bounds=[16, 9.5], pattern="hour"),  # hide hours outside of 9.30am-4pm
                # dict(values=["2019-12-25", "2020-12-24"])  # hide holidays (Christmas and New Year's, etc)
            ]
        )
    else:
        fig.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[
                # NOTE: Below values are bound (not single values), ie. hide x to y
                dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
                dict(bounds=[16, 9.5], pattern="hour"),  # hide hours outside of 9.30am-4pm
                # dict(values=["2019-12-25", "2020-12-24"])  # hide holidays (Christmas and New Year's, etc)
            ]
        )

    # Show
    # fig.show()

    return fig

def candles2(data):
    # declare figure
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'], name='market data'))

    # Add titles
    """fig.update_layout(
        #title='Uber live share price evolution',
        yaxis_title='Курс акций в долларах')
"""
    # Делаем кнопки для навигации
    """ fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                #dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1month", step="month", stepmode="backward"),
                dict(step="all")
            ])
        )
    ) """

    # настраиваем размер графика
    fig.update_layout(autosize=True,
                      width=1000,
                      height=700, )

    # убираем разрывы меежду данными. Чтобы график был сплошной. То есть убираем выходные и часы, когда торговля не идет
    fig.update_xaxes(
        rangeslider_visible=False,
        rangebreaks=[
            # NOTE: Below values are bound (not single values), ie. hide x to y
            dict(bounds=["sat", "mon"]),  # hide weekends, eg. hide sat to before mon
            # dict(bounds=[16, 9.5], pattern="hour"),  # hide hours outside of 9.30am-4pm
            # dict(values=["2019-12-25", "2020-12-24"])  # hide holidays (Christmas and New Year's, etc)
        ]
    )

    # Show
    # fig.show()

    return fig


def get_quotes(ticker, period, interval):
    data = yf.download(tickers=ticker, period=period, interval=interval)

    if data.size != 0:
        return data
    else:
        return 'неправильные данные'


goog_token = "ef44e796dd82495d9b0ac4ed58354d70"
hub_token = "c33nijqad3i8edlc7t50"
polygon_token = "ZrbA9bOMxg8Nf2qyV14nzV1DLk65mFip"

def get_news_headlines2(ticker):
    global polygon_token
    url = (f'https://api.polygon.io/v2/reference/news?limit=10&order=descending&sort=published_utc&ticker={ticker}&published_utc.gte=2021-04-26&apiKey={polygon_token}')
    r = requests.get(url).json()['results']
    a = []
    for i in r:
        a.append(i['title'] + ' : ' + i['article_url'])
    return a


token = '1879589421:AAEjb6TKhChdjsLIEDFE_3lKJL3p8IfBHL4'

bot = telebot.TeleBot(token)  # тут токен типа удалить бы надо


@bot.message_handler(commands=['start'])
def send_start(message):
    resp = register_client(message.from_user.id)
    msg = bot.send_message(message.from_user.id, text=resp + message.from_user.first_name)
    send_keyboard(message)


@bot.message_handler(commands=['menu'])
def send_keyboard(message, text="Добро пожаловать в главное меню"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
    itembtn1 = types.KeyboardButton('Портфель')  # создадим кнопку
    itembtn2 = types.KeyboardButton('Биржа')
    itembtn3 = types.KeyboardButton('Рекорды')
    itembtn4 = types.KeyboardButton("Аналитика")
    itembtn5 = types.KeyboardButton('Ничего не надо, адыхай')
    keyboard.add(itembtn1, itembtn2)  # добавим кнопки 1 и 2 на первый ряд
    keyboard.add(itembtn3, itembtn4, itembtn5)  # добавим кнопки 3, 4, 5 на второй ряд
    # но если кнопок слишком много, они пойдут на след ряд автоматически
    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)
news=0

@bot.message_handler(content_types=['text'])
def responser(message, text='а там армяне в нарды играют'):
    global stock
    global action
    global quantity
    global fuckt
    global keyboardbig
    global price
    global news
    keyboardbig = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
    itembtn1 = types.KeyboardButton('AAPL')  # создадим кнопку
    itembtn2 = types.KeyboardButton('GOOG')
    itembtn3 = types.KeyboardButton('AMZN')
    itembtn4 = types.KeyboardButton("KO")
    itembtn5 = types.KeyboardButton('TSLA')
    itembtn6 = types.KeyboardButton('SPCE')
    itembtn7 = types.KeyboardButton('GME')
    itembtn8 = types.KeyboardButton('YNDX')
    keyboardbig.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5,
                    itembtn6, itembtn7, itembtn8, types.KeyboardButton('/menu'))
    fuckt = 0
    if message.text == 'Портфель':
        fuckt = 1

        stocks_to_string(message.from_user.id, message)

        bot.send_message(message.chat.id,
                         text='Чтобы совершить операцию с акциями из вашего портфеля, введите интересующий вас тикер',
                         reply_markup=keyboardbig)

    if message.text == 'Биржа':
        fuckt = 1
        msg = bot.send_message(message.from_user.id, text='Вы пришли на Быржу',
                               reply_markup=keyboardbig)

    if message.text == 'Рекорды':
        fuckt = 1
        bot.send_message(message.chat.id, text=f'Открываете книгу рекордов, {text}')

    if message.text == 'Аналитика':
        fuckt = 1
        news = 1
        bot.send_message(message.chat.id, text=f'Заходите вы в отдел аналитики, {text}')
        bot.send_message(message.chat.id, text='Самый главный армянин подходит и спрашивает:')
        bot.send_message(message.chat.id, text='Дарагой, по какой акции новости интересуют?',reply_markup=keyboardbig)
    if message.text == 'Ничего не надо, адыхай':
        fuckt = 1
        bot.send_photo(message.chat.id, 'https://sun9-23.userapi.com/impg/fJfATGZ1yJNblzkRvGXfyqcO081FPqebcqENOg/12uvlgcKZ24.jpg?size=1811x1017&quality=96&sign=505da16c7dfb0bf60b0d32669713e90a&type=album')
        bot.send_message(message.chat.id, text='адыхаю')


    if message.text.split(' ')[0] in stocks_list and news == 0:
        fuckt = 1
        try:
            ticker, period, interval = message.text.split()
            if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
                result_photo = candles(get_quotes(ticker, period, interval)).to_image(format="png", engine="kaleido")
                bot.send_photo(message.chat.id, result_photo)
            else:
                result_photo = candles(get_quotes(ticker, period, interval), type2=True).to_image(format="png",
                                                                                                  engine="kaleido")
                bot.send_photo(message.chat.id, result_photo)
        except:
            result_photo = candles2(get_quotes(message.text.split(' ')[0], '1d', '1m')).to_image(format="png",
                                                                                                 engine="kaleido")
            bot.send_photo(message.chat.id, result_photo)
        price = pricechanger(message.text)
        keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
        itembtn1 = types.KeyboardButton(f'BUY {message.text}')  # создадим кнопку
        itembtn2 = types.KeyboardButton(f'SELL {message.text}')
        itembtn5 = types.KeyboardButton(f'{message.text} 7d 1m')  # создадим кнопку
        itembtn6 = types.KeyboardButton(f'{message.text} 30d 1h')
        itembtn7 = types.KeyboardButton(f'{message.text} 100d 1h')  # создадим кнопку
        itembtn8 = types.KeyboardButton(f'{message.text} 360d 1h')
        itembtn3 = types.KeyboardButton('Биржа')
        itembtn4 = types.KeyboardButton('/menu')
        keyboard.add(itembtn1, itembtn2, itembtn5, itembtn6, itembtn7, itembtn8)
        keyboard.add(itembtn3, itembtn4)
        msg = bot.send_message(message.from_user.id,
                               text=f'Текущая цена: {price}, можно выбрать формат сделки или отрегулировать размер графика, также размер графика можно изменить вручную по запросу вида: "тикер_период(в днях)_интервал(в минутах или часах)"',
                               reply_markup=keyboard)

    if message.text[0:3] == 'BUY':
        fuckt = 1
        stock = message.text[4::]
        if stock not in stocks_list:
            bot.send_message(message.chat.id, text='Фигню сказал')
        else:
            keyboard = types.ReplyKeyboardMarkup(row_width=2)
            for i in range(3):
                keyboard.add(types.KeyboardButton(str(5 * 10 ** i)), types.KeyboardButton(str(10 * 10 ** i)))
            keyboard.add(types.KeyboardButton('/menu'))
            bot.send_message(message.chat.id, text=f'Введите количество {stock}', reply_markup=keyboard)
            action = 1

    if message.text[0:4] == 'SELL':
        fuckt = 1
        stock = message.text[5::]
        if stock not in stocks_list:
            bot.send_message(message.chat.id, text='Фигню сказал')
        else:
            bot.send_message(message.chat.id, text=f'Введите количество {stock}')
            keyboard = types.ReplyKeyboardMarkup(row_width=2)
            for i in range(3):
                keyboard.add(types.KeyboardButton(str(5 * 10 ** i)), types.KeyboardButton(str(10 * 10 ** i)))
            keyboard.add(types.KeyboardButton('/menu'))
            bot.send_message(message.chat.id, text=f'Введите количество {stock}', reply_markup=keyboard)
            action = 0
    if message.text.isdigit():
        fuckt = 1
        if stock in stocks_list:
            quantity = int(message.text)
            ans = 'купить' if action == 1 else 'продать'
            vol = quantity * price
            vol_s = '{:>10.2f}'.format(vol)
            bot.send_message(message.chat.id,
                             text=f'Итак, вы хотите {ans} *{str(quantity)}* {stock} на сумму *{vol}*  bucks. Подтвердите выбор',
                             parse_mode='Markdown')
            keyboard = types.ReplyKeyboardMarkup(row_width=2)
            keyboard.add(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
            msg = bot.send_message(message.from_user.id,
                                   text='Если вы ошиблись в количестве акций, просто введите другое число',
                                   reply_markup=keyboard)
        else:
            bot.send_message(message.from_user.id,
                             text='Вы не выбрали акцию')
            send_keyboard(message)

    if message.text == 'Да' and (stock, action, quantity) != ('', -1, 0):
        fuckt = 1
        if action == 1:
            buy(message.from_user.id, stock, quantity)
        else:
            sell(message.from_user.id, stock, quantity)
        (stock, action, quantity) = ('', -1, 0)

        stocks_to_string(message.from_user.id, message)

        bot.send_message(message.chat.id,
                         text='Чтобы совершить операцию с акциями из вашего портфеля, введите интересующий вас тикер',
                         reply_markup=keyboardbig)
        if message.text == 'Нет':
            (stock, action, quantity) = ('', -1, 0)
            send_keyboard(message)
    if message.text == 'AEZAKMI':
        fuckt=1
        bot.send_message(message.chat.id,
                         text=str(clients)+' razdel ' +str(stocks),
                         reply_markup=keyboardbig)
    if message.text in stocks_list and  news == 1:
        fuckt=1
        newslist=get_news_headlines2(message.text)
        for i in range(min(len(newslist), 3)):
            bot.send_message(message.chat.id,text=newslist[i])
        news=0
    if fuckt == 0:
        bot.send_message(message.chat.id, text='Фигню сказал')
        send_keyboard(message)


bot.infinity_polling()