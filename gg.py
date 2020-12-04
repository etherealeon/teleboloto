import telebot
from telebot import types
from keyboa import keyboa_maker
from geocode import getCoords
from loll import Configs
import re
from users import user_dict
from weatherapi import getCurrentWeather

bot = telebot.TeleBot(Configs.teleboloto)

isRunning: bool = False


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
        self.step = 0


def add_user(mci):
    user = User()
    if mci not in user_dict.keys():
        user_dict[mci] = user


def chek(message, txt, next_f, *cont_types):
    for cont_type in cont_types:
        if message.content_type == cont_type:
            return True

    msg = bot.reply_to(message, txt)
    bot.register_next_step_handler(msg, next_f)
    return False


def to_begin(mci):
    add_user(mci)
    text_oa = 'Кажется, данные о тебе не сохранились.\nПожалуйста, пройди регистрацию заново\n' \
              'Как мне тебя называть?'
    msg = bot.send_message(mci, text_oa, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, acquaintanceSex)


@bot.message_handler(commands=['start'])
def start_message(message):
    # todo Forbid starting two interactions from one user simultaneously
    # global isRunning
    # if not isRunning:
    add_user(message.chat.id)
    text_hi = "Привет!\nЯ бот, который еще нихера не умеет, но, давай знакомиться!\nКак мне тебя называть?"
    msg = bot.reply_to(message, text_hi, reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, acquaintanceSex)
    # isRunning = True


# else:
# return


def acquaintanceSex(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'wow buddy dat s pretty cool but I need ur NAME', acquaintanceSex, 'text'):
            return

        current_user = user_dict.get(message.chat.id)
        current_user.name = message.text
        keyboard_sex = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_sex.add('Женский').add('Мужской').add('Я небинарное чудо')
        text_sex = "Принято, %s\nУкажите, пожалуйста, Ваш пол(sex)" % current_user.name
        msg = bot.reply_to(message, text_sex, reply_markup=keyboard_sex)
        bot.register_next_step_handler(msg, acquaintanceHeat)
    else:
        to_begin(message.chat.id)


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
        to_begin(message.chat.id)


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
            text_loc = "ПРЕВОСХОДНО! А живешь ты где?"
            keyboard_loc = types.ReplyKeyboardMarkup(resize_keyboard=True)
            key_loc = types.KeyboardButton(text='Отправить геолокацию', request_location=True)
            keyboard_loc.add(key_loc).add('Хочу погоду в другом городе')
            msg = bot.reply_to(message, text_loc, reply_markup=keyboard_loc)
            bot.register_next_step_handler(msg, ProcLoc)
            return
        else:
            msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
            bot.register_next_step_handler(msg, acquaintanceLoc)
            return
    else:
        to_begin(message.chat.id)


def ProcLoc(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'I need ur city or location.........pleeease', ProcLoc, 'text', 'location'):
            return

        elif message.location is not None:
            current_user.lon = message.location.longitude
            current_user.lat = message.location.latitude
            return
        elif message.text == 'Хочу погоду в другом городе':
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
        to_begin(message.chat.id)


def AdvGeoCode(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', AdvGeoCode, 'text'):
            return
        current_user = user_dict.get(message.chat.id)
        current_user.city = message.text
        try:
            list_txt = "Выберите Свой город из списка пож:"
            list_cities = keyboa_maker(items=getCoords(current_user.city))
            msg = bot.reply_to(message, list_txt, reply_markup=list_cities)
            bot.register_next_step_handler(msg, Coords)
        except ValueError:
            no_city_txt = 'Похоже, я не могу найти такой город\nПопробуй по-другому пож'
            msg = bot.reply_to(message, no_city_txt, reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, AdvGeoCode)
    else:
        to_begin(message.chat.id)


@bot.callback_query_handler(func=lambda call: (bool(re.search(r"\d\d[.]\d{6}\s\d\d[.]\d{6}",
                                                              call.data))) or (call.data == 'Wrong city'))
def Coords(call):
    print('why')
    current_user = user_dict.get(call.from_user.id)
    if current_user is not None:
        try:
            if call.data == 'Wrong city':
                msg = bot.send_message(call.from_user.id, "Ну, попробуй ввести город еще раз))",
                                       reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, AdvGeoCode)
                current_user.step = 1
                return

            elif bool(re.search(r"\d\d[.]\d{6}\s\d\d[.]\d{6}", call.data)):
                current_user.lon = float(call.data.split(' ')[0])
                current_user.lat = float(call.data.split(' ')[1])
                keyboard_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard_main.add('Погоду сейчас').add('Прогноз на неделю').add('Почасовой прогноз на сегодня')
                msg = bot.send_message(call.from_user.id, "Ура!\nВот и познакомились.\nТеперь выбери,чего же ты хочешь",
                                       reply_markup=keyboard_main)
                bot.register_next_step_handler(msg, WeatherConfigs)
                current_user.step = 1
                return

        except AttributeError as e:
            if current_user.step == 1:
                return
            else:
                msg = bot.send_message(call.from_user.id, 'Пока не выберешь город из списка ничего не произойдет..')
                bot.register_next_step_handler(msg, Coords)
                return
    else:
        to_begin(call.from_user.id)
        return


def WeatherConfigs(message):
    print('f')
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if message.text == 'Погоду сейчас':
            cur_text = getCurrentWeather(current_user.lat, current_user.lon)
            bot.send_message(message.chat.id, cur_text)
    else:
        to_begin(message.chat.id)


bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()
bot.polling(none_stop=True)
