import telebot
from telebot import types
import re
from keyboa import keyboa_maker

from geocode import getCoords
from loll import Configs
from users import user_dict
from weatherapi import getCurrentWeather, getTomorrowWeather, getClothNow, getClothTomorrow, bestDay

bot = telebot.TeleBot(Configs.teleboloto)


def keyboard_main():
    keyb_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyb_main.add('Погоду сейчас', 'Прогноз на завтра').add('Прогноз на неделю') \
        .add('Что надеть cейчас?', 'Что надеть завтра?').add('Когда пойти гулять?')
    return keyb_main


def keyboard_sex():
    keyb_sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyb_sex.add('Женский').add('Мужской').add('Я небинарное чудо')
    return keyb_sex


# todo add Urets's  wonderful voice answ
# todo make HI message
# todo make help message
# todo choose avatar pic


class User:
    def __init__(self):
        self.name = ''
        self.heat = 0
        self.sex = ''
        self.lat = ''
        self.lon = ''
        self.city = ''
        self.rain = None
        self.car = None
        self.running = False


def add_user(mci):
    user = User()
    if mci not in user_dict.keys():
        user_dict[mci] = user


def chek(message, txt, next_f, *cont_types):
    if message.content_type == 'text' and message.text == '/start':
        to_begin(message.chat.id, message.from_user.first_name)
        return
    for cont_type in cont_types:
        if message.content_type == cont_type:
            return True

    msg = bot.reply_to(message, txt)
    bot.register_next_step_handler(msg, next_f)
    return False


def to_begin(mci, name):
    add_user(mci)
    bot.clear_step_handler_by_chat_id(chat_id=mci)
    current_user = user_dict.get(mci)
    current_user.name = name
    text_oa = f'{name},кажется, данные о тебе не сохранились.\nПознакомимся еще разОчек?)' \
              f' Укажите, пожалуйста, Ваш пол(sex)'
    msg = bot.send_message(mci, text_oa, reply_markup=keyboard_sex())
    bot.register_next_step_handler(msg, acquaintanceHeat)


def common_weather_fun(mci, name):
    current_user = user_dict.get(mci)
    if current_user is not None and current_user.running is False:
        return True
    else:
        bot.send_message(mci, 'Голубчик, у меня нет твоих данных:(\nПройди, пожалуйста, регистрацию')
        to_begin(mci, name)
        return False


@bot.message_handler(commands=['start'])
def start_message(message):
    add_user(message.chat.id)
    current_user = user_dict.get(message.chat.id)
    current_user.name = message.from_user.first_name
    if current_user.name is None:
        current_user.name = 'мое чудо'
    if not current_user.running:
        current_user.running = True
        text_hi = f"Здравствуй, {current_user.name}!\nЯ бот, давай знакомиться!\nУкажите, пожалуйста, Ваш пол(sex)"
        msg = bot.reply_to(message, text_hi, reply_markup=keyboard_sex())
        bot.register_next_step_handler(msg, acquaintanceHeat)


def acquaintanceHeat(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'wow buddy dat s pretty cool but I need ur SEX', acquaintanceHeat, 'text'):
            return
        sex = message.text
        if (sex == 'Женский') or (sex == 'Мужской'):
            current_user.sex = sex
        elif sex == 'Я небинарное чудо':
            text_sex2 = 'В семье не без урода. ЧТОШ....Ну а юбки и платья вы носите?'
            keyboard_yn = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_yn.add("Дa", "Hет")
            msg = bot.reply_to(message, text_sex2, reply_markup=keyboard_yn)
            bot.register_next_step_handler(msg, acquaintanceHeat)
            return

        elif sex == "Дa" or sex == "Hет":
            current_user.sex = 'Женский'
            if sex == "Нет":
                current_user.sex = 'Мужской'
        else:
            msg = bot.reply_to(message, 'Пол введи дебил\n КНОПАЧКАМИ')
            bot.register_next_step_handler(msg, acquaintanceHeat)

        if (current_user.sex == 'Женский') or (current_user.sex == 'Мужской'):
            keyboard_heat = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard_heat.add('Я мезляч').add('Я горяч').add('Чё? Я норм.')
            msg = bot.reply_to(message, "Хорошо.\nНу тут одно из ТРЁХ", reply_markup=keyboard_heat)
            bot.register_next_step_handler(msg, acquaintanceLoc)
            return
    else:
        to_begin(message.chat.id, message.from_user.first_name)


def acquaintanceLoc(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', acquaintanceLoc, 'text'):
            return

        if message.text == 'Я мезляч' or 'Я горяч' == message.text or 'Чё? Я норм.' == message.text:
            if message.text == 'Я горяч':
                current_user.heat = 1
            if message.text == 'Я горяч':
                current_user.heat = -1
            text_loc = "ПРЕВОСХОДНО! А погода тебе где нужна?"
            keyboard_loc = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key_loc = types.KeyboardButton(text='Отправить геолокацию', request_location=True)
            keyboard_loc.add(key_loc).add('Введу название')
            msg = bot.reply_to(message, text_loc, reply_markup=keyboard_loc)
            bot.register_next_step_handler(msg, ProcLoc)
            return
        else:
            msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
            bot.register_next_step_handler(msg, acquaintanceLoc)
            return
    else:
        to_begin(message.chat.id, message.from_user.first_name)


def ProcLoc(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'I need ur city or location.........pleeease', ProcLoc, 'text', 'location'):
            return

        elif message.location is not None:
            current_user.lon = float(message.location.longitude)
            current_user.lat = float(message.location.latitude)
            bot.send_message(message.chat.id, "Ура!\nВот и познакомились.\nТеперь выбери,чего же ты хочешь",
                             reply_markup=keyboard_main())
            current_user.running = False
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            return
        elif message.text == 'Введу название':
            txt = 'Хорошо.\nНапиши, пожалуйста, название своего города(села, деревни) или откуда ты там вообще...' \
                  '\nНапример,\nМосква'
            msg = bot.reply_to(message, txt, reply_markup=None)
            bot.register_next_step_handler(msg, AdvGeoCode)
            return

        else:
            msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
            bot.register_next_step_handler(msg, ProcLoc)
            return
    else:
        to_begin(message.chat.id, message.from_user.first_name)


def AdvGeoCode(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', AdvGeoCode, 'text'):
            return
        current_user.city = message.text
        try:
            list_txt = "Выберите Свой город из списка пож:"
            list_cities = keyboa_maker(items=getCoords(current_user.city))
            msg = bot.reply_to(message, list_txt, reply_markup=list_cities)
            bot.register_next_step_handler(msg, Coords)
        except ValueError:
            no_city_txt = 'Похоже, я не могу найти ТАКОЕ \nПопробуй по-другому пож'
            msg = bot.reply_to(message, no_city_txt, reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, AdvGeoCode)
    else:
        to_begin(message.chat.id, message.from_user.first_name)


@bot.callback_query_handler(func=lambda call: (bool(re.search(r".*\d+[.]\d{4,6}\s.*\d+[.]\d{4,6}",
                                                              call.data))) or (call.data == 'Wrong city'))
def Coords(call):
    print('blya')
    current_user = user_dict.get(call.from_user.id)
    if current_user is not None:
        try:
            bot.edit_message_reply_markup(call.from_user.id, message_id=call.message.message_id, reply_markup=None)
            if call.data == 'Wrong city':
                msg = bot.send_message(call.from_user.id, "Ну, попробуй ввести еще раз)))))))))\n"
                                                          "может, по-другому как-то))",
                                       reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, AdvGeoCode)
                return

            elif bool(re.search(r".*\d+[.]\d{4,6}\s.*\d+[.]\d{4,6}", call.data)):
                current_user.lon = float(call.data.split(' ')[0])
                current_user.lat = float(call.data.split(' ')[1])
                bot.send_message(call.from_user.id, "Ура!\nВот и познакомились.\nТеперь выбери,чего же ты хочешь",
                                 reply_markup=keyboard_main())
                current_user.running = False
                bot.clear_step_handler_by_chat_id(chat_id=call.from_user.id)
                return

        except AttributeError as e:
            print(e)
            msg = bot.send_message(call.from_user.id, 'Пока не выберешь что-то из списка выше ничего не произойдет..')
            bot.register_next_step_handler(msg, Coords)
            return
    else:
        to_begin(call.from_user.id, call.from_user.first_name)
        return


@bot.message_handler(regexp='Погоду сейчас')
def weatherNow(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        current_user = user_dict.get(message.chat.id)
        cur_text = getCurrentWeather(current_user.lat, current_user.lon)
        bot.send_message(message.chat.id, cur_text)


@bot.message_handler(regexp='Прогноз на завтра')
def weatherTom(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        current_user = user_dict.get(message.chat.id)
        tom_text = getTomorrowWeather(current_user.lat, current_user.lon)
        bot.send_message(message.chat.id, tom_text)


@bot.message_handler(regexp='Что надеть cейчас?')
def ClothNow(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        current_user = user_dict.get(message.chat.id)
        now_cloth = getClothNow(current_user.lat, current_user.lon, current_user.sex, current_user.heat)
        bot.send_message(message.chat.id, now_cloth)


@bot.message_handler(regexp='Что надеть завтра?')
def ClothTom(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        current_user = user_dict.get(message.chat.id)
        tom_cloth = getClothTomorrow(current_user.lat, current_user.lon, current_user.sex, current_user.heat)
        bot.send_message(message.chat.id, tom_cloth)


@bot.message_handler(regexp='Когда пойти гулять?')
def weatherNow(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        current_user = user_dict.get(message.chat.id)
        cur_text = bestDay(current_user.lat, current_user.lon)
        bot.send_message(message.chat.id, cur_text)


@bot.message_handler(content_types=['text'])
def all_message(message):
    if common_weather_fun(message.chat.id, message.from_user.first_name):
        bot.send_message(message.chat.id, 'Я тебя не понимайт')


if __name__ == '__main__':
    while 1:
        bot.enable_save_next_step_handlers(delay=2)
        # bot.load_next_step_handlers()
        bot.polling(none_stop=True)
