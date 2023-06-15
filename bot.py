import requests
import random
import telebot
import json
from config import token, api_key
from telebot import types
from bs4 import BeautifulSoup as b

URL = 'https://www.anekdot.ru/best/anekdot/0614/'
def parser(url): # создаем функцию, кот будет всё выкачивать
    r = requests.get(url)
    soup = b(r.text, 'html.parser')
    anekdots = soup.find_all('div', class_='text')
    return [c.text for c in anekdots]

list_of_jokes = parser(URL)
random.shuffle(list_of_jokes)


# создаем экземпляр бота
bot = telebot.TeleBot(token)
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}! Нажимай /menu и запускай бота)')
    #bot.send_message(message.chat.id, 'или жми /menu')


@bot.message_handler(commands=['menu'])
def button_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True) # этот объект предоставляет клавиатуру с опциями ответа
    item1 = types.KeyboardButton("Анегдоты")   # вот так содаем кнопки, каждая в отдельной переменной
    item2 = types.KeyboardButton("ПП-рецепты")
    item3 = types.KeyboardButton("Погода")
    markup.add(item1, item2, item3)  # дальше к клавиатуре добавим нашу кнопку
    bot.send_message(message.chat.id, 'Жми кнопку "Анегдоты" и получай шутку;) или читай "ПП-рецепты"', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def message_replay(message):
    if message.text == "Анегдоты": # по нажатию на кнопку анегдоты выдаем функцию jokes
        bot.send_message(message.chat.id, list_of_jokes[0])  # отправляем шутку
        del list_of_jokes[0] # удаляем из списка, чтобы не повторялись
    elif message.text == "ПП-рецепты":
        bot.send_message(message.chat.id, '[ПП-рецепты](https://1000.menu/catalog/pp-recepty)', parse_mode='Markdown')
    elif message.text == "Погода":
        bot.send_message(message.chat.id, 'Введите город: ')
        bot.register_next_step_handler(message, ask_city_name)


def ask_city_name(message):
    city_name = message.text
    weather = get_weather(city_name, api_key)
    bot.send_message(message.chat.id, weather)

def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    if data["cod"] == "404":
        return "Город не найден. Проверьте правильность написание города или выберите другой."

    temperature = round(data["main"]["temp"], 1)
    temperature_celsius = round((temperature - 273.15), 1)
    humidity = data["main"]["humidity"]

    weather_info = f"Погода в {city_name}:\nТемпература: {temperature_celsius} \nВлажность: {humidity}%"
    return weather_info



bot.polling(none_stop=True, interval=0)