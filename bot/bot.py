"""Реализация общения бота с полльзователями"""
from io import BytesIO
import telebot
from telebot import types
from PIL import Image
import requests

TOKEN = ''  # здась должен быть токен бота
bot = telebot.TeleBot(TOKEN)

films_data = {}
current_films = {}

filters = {}

approved = {}
kworum = {}

film_types = {
    'tv-series': 'Сериал',
    'movie': 'Фильм',
    'animated-series': 'Анимационный сериал',
    'cartoon': 'Мультфильм',
    'anime': 'Анимэ'
}


def get_genres_as_str(film_genres):
    """Парсинг выходных данных для получения жанров"""

    genres_names = [genre['name'] for genre in film_genres]
    return ', '.join(genres_names)


def get_countries_as_str(film_countries):
    """Парсинг выходных данных для получения стран производителей"""

    countries_names = [country['name'] for country in film_countries]
    return ', '.join(countries_names)


def parse_url(chat_id: str):
    """Парсинг url для получения фильтров пользователя"""

    url = filters[chat_id]
    if url.find('isSeries=true') != -1:
        type_of_film = 'сериал'
    elif url.find('isSeries=false') != -1:
        type_of_film = 'фильм'
    else:
        type_of_film = 'не важно'

    if url.find('genres.name=') != -1:
        genre_of_film = url.split('genres.name=')[1].split('&')[0]
    else:
        genre_of_film = 'не важно'

    if url.find('year=') != -1:
        release_years = url.split('year=')[1]
    else:
        release_years = 'не важно'

    game_filter = "Ваши фильтры:" + \
                  "\nТип - " + type_of_film + \
                  "\nЖанр - " + genre_of_film + \
                  "\nГоды релиза - " + release_years

    return game_filter


def make_caption(film):
    """Составление описания к фильму/сериалу"""

    type_of_film = film_types[film['type']]
    caption = '*' + film['name'] + '*' + '\n'
    caption += "*Тип:* " + type_of_film + '\n'
    caption += "*Жанры:* " + get_genres_as_str(film['genres']) + '\n'
    caption += "*Страна производства:* " + get_countries_as_str(film['countries']) + '\n'
    caption += "*Год релиза:* " + str(film['year']) + '\n'
    caption += "*Рейтинг IMDB:* " + str(film['rating']['imdb']) + '\n'
    caption += "*Описание:* " + str(film['description']).split('\n', maxsplit=1)[0]
    return caption


def make_request(chat_id: str):
    """Произведение API запроса к кинопоиску"""

    headers = {'X-API-KEY': ''}  # здась должен быть токен
    url = filters[chat_id]
    response = requests.get(url, headers=headers, timeout=30)

    data = response.json()

    current_films[chat_id] = data["docs"].copy()

    make_recommendation(chat_id)


def make_recommendation(chat_id: str, recent_movie: str = None):
    """ВЫбор фильма, чтобы показать пользователю"""
    approved[chat_id] = set()
    kworum[chat_id] = set()
    flag = False
    film_found = False
    if not recent_movie:
        flag = True
    for film in current_films[chat_id]:
        if film['name'] == recent_movie:
            flag = True
            continue
        if not flag:
            continue
        caption = make_caption(film)

        photo_resp = requests.get(film['poster']['url'], timeout=30)
        sent_message = None
        try:
            image = Image.open(BytesIO(photo_resp.content))
            sent_message = bot.send_photo(chat_id, photo=image, caption=caption,
                                          parse_mode='Markdown')
        except telebot.apihelper.ApiTelegramException:
            print("can't load photo")
            try:
                photo_resp = requests.get(film['backdrop']['url'], timeout=30)
                image = Image.open(BytesIO(photo_resp.content))
                sent_message = bot.send_photo(chat_id, photo=image, caption=caption,
                                              parse_mode='Markdown')
            except telebot.apihelper.ApiTelegramException:
                continue
        film_found = True

        markup = types.InlineKeyboardMarkup(row_width=2)
        item_1 = types.InlineKeyboardButton(text="Да",
                                            callback_data=f"choice yes {sent_message.id}")
        item_2 = types.InlineKeyboardButton(text="Нет",
                                            callback_data=f"choice no {sent_message.id}")
        markup.add(item_1, item_2, )
        bot.send_message(chat_id, f"Хотите посмотреть {film['name']} ?", reply_markup=markup)
        break
    if not film_found or not current_films[chat_id]:
        bot.send_message(chat_id, "К сожалению, подборка закончилась, начните игру заново")
        start_game(chat_id)


def choose_genre(chat_id: str):
    """Предложение выбрать жанр из списка"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    item_1 = types.InlineKeyboardButton(text="Криминал", callback_data="genre Криминал")
    item_2 = types.InlineKeyboardButton(text="Детектив", callback_data="genre Детектив")
    item_3 = types.InlineKeyboardButton(text="Драма", callback_data="genre Драма")
    item_4 = types.InlineKeyboardButton(text="Комедия", callback_data="genre Комедия")
    item_5 = types.InlineKeyboardButton(text="Ужасы", callback_data="genre Ужасы")
    item_6 = types.InlineKeyboardButton(text="Фантастика", callback_data="genre Фантастика")
    item_7 = types.InlineKeyboardButton(text="Мультфильм", callback_data="genre Мультфильм")
    item_8 = types.InlineKeyboardButton(text="Приключения", callback_data="genre Приключения")
    item_9 = types.InlineKeyboardButton(text="Боевик", callback_data="genre Боевик")
    item_10 = types.InlineKeyboardButton(text="Триллер", callback_data="genre Триллер")
    item_11 = types.InlineKeyboardButton(text="Мелодрама", callback_data="genre Мелодрама")
    item_12 = types.InlineKeyboardButton(text="Мюзикл", callback_data="genre Мюзикл")
    item_13 = types.InlineKeyboardButton(text="Не важно", callback_data="genre nothing")
    markup.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7,
               item_8, item_9, item_10, item_11, item_12, item_13)
    bot.send_message(chat_id, 'Выберите жанр:', reply_markup=markup)


def choose_years(chat_id: str):
    """Предложение выбрать годы релиза из списка"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    item_1 = types.InlineKeyboardButton(text="1950-1960", callback_data="years 1950-1960")
    item_2 = types.InlineKeyboardButton(text="1961-1970", callback_data="years 1961-1970")
    item_3 = types.InlineKeyboardButton(text="1971-1980", callback_data="years 1971-1980")
    item_4 = types.InlineKeyboardButton(text="1981-1990", callback_data="years 1981-1990")
    item_5 = types.InlineKeyboardButton(text="1991-2000", callback_data="years 1991-2000")
    item_6 = types.InlineKeyboardButton(text="2001-2005", callback_data="years 2001-2005")
    item_7 = types.InlineKeyboardButton(text="2006-2010", callback_data="years 2006-2010")
    item_8 = types.InlineKeyboardButton(text="2011-2015", callback_data="years 2011-2015")
    item_9 = types.InlineKeyboardButton(text="2016-2020", callback_data="years 2016-2020")
    item_10 = types.InlineKeyboardButton(text="2021-2023", callback_data="years 2021-2023")
    item_11 = types.InlineKeyboardButton(text="Не важно", callback_data="years nothing")
    markup.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7, item_8,
               item_9, item_10, item_11)
    bot.send_message(chat_id, 'Выберите годы релиза:', reply_markup=markup)


def start_game(chat_id: str):
    """Начать игру - предложение выбрать тип"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_1 = types.InlineKeyboardButton(text="Сериал", callback_data="type series")
    item_2 = types.InlineKeyboardButton(text="Фильм", callback_data="type movie")
    item_3 = types.InlineKeyboardButton(text="Не важно", callback_data="type nothing")
    markup.add(item_1, item_2, item_3)
    bot.send_message(chat_id, 'Выберите тип:', reply_markup=markup)


@bot.message_handler(commands=['start'])
def start_bot(message):
    """Функция start"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_1 = types.InlineKeyboardButton(text="Начать игру", callback_data="start game")
    markup.add(item_1)
    bot.send_message(message.chat.id, 'Привет ✌️ Нажми на кнопку, чтобы начать игру!',
                     reply_markup=markup)


@bot.message_handler(commands=['info'])
def get_info(message):
    """Функция info"""
    bot.send_message(message.chat.id,
                     'Чтобы включить игру, напишите /start_game')


@bot.message_handler(commands=['start_game'])
def button_message(message):
    """Функция начала игры через /start_game"""
    start_game(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def call_response(call):
    """Функция обработки inline кнопок"""
    if call.data.startswith("type"):
        try:
            bot.delete_message(call.message.chat.id, call.message.id)
        except telebot.apihelper.ApiTelegramException:
            pass
        type_movie = call.data.split()[1]
        filters[call.message.chat.id] = "https://api.kinopoisk.dev/v1.4/"
        filters[call.message.chat.id] += "movie?"

        if type_movie == "series":
            filters[call.message.chat.id] += "isSeries=true&"
        elif type_movie == "movie":
            filters[call.message.chat.id] += "isSeries=false&"

        choose_genre(call.message.chat.id)

    elif call.data.startswith("genre"):
        genre = call.data.split()[1].lower()
        if genre != 'nothing':
            filters[call.message.chat.id] += "genres.name=" + genre + '&'
        # bot.send_message(call.message.chat.id, parse_url(call.message.chat.id))
        bot.delete_message(call.message.chat.id, call.message.id)
        choose_years(call.message.chat.id)
        # make_request(call.message.chat.id)

    elif call.data.startswith("years"):
        years = call.data.split()[1]
        if years != 'nothing':
            filters[call.message.chat.id] += "year=" + years
        bot.send_message(call.message.chat.id, parse_url(call.message.chat.id))
        bot.delete_message(call.message.chat.id, call.message.id)
        make_request(call.message.chat.id)

    elif call.data.startswith("choice"):
        choice = call.data.split()[1]
        description_id = call.data.split()[2]
        recent_movie = call.message.text.split('Хотите посмотреть ')[1].split(' ?')[0]
        approved[call.message.chat.id].add(call.from_user.id)
        if choice == 'yes':
            kworum[call.message.chat.id].add(call.from_user.id)
        count_members = bot.get_chat_member_count(call.message.chat.id) - 1
        if len(approved[call.message.chat.id]) == count_members:
            if len(kworum[call.message.chat.id]) == count_members:
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_message(call.message.chat.id, f"Отлично! Выбор пал на {recent_movie}")
            else:
                bot.send_message(call.message.chat.id, f"{recent_movie} не подошёл:(")

                bot.delete_message(call.message.chat.id, call.message.id)
                bot.delete_message(call.message.chat.id, description_id)

                make_recommendation(call.message.chat.id, recent_movie)

    elif call.data == "start game":
        start_game(call.message.chat.id)


bot.polling(none_stop=True, interval=0)
