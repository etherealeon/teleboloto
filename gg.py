import telebot
from telebot import types
from keyboa import keyboa_maker
from geocode import getCoords
from loll import Configs
import re
from users import user_dict

bot = telebot.TeleBot(Configs.teleboloto)
# userStep = {}   so they won't reset every time the bot restarts


class User:
    def __init__(self):
        self.name = ''
        self.heat = True
        self.sex = ''
        self.loc = ''
        self.city = ''
        self.rain = None
        self.car = None


@bot.message_handler(commands=['start'])
def start_message(message):
    user = User()
    if message.chat.id not in user_dict.keys():
        user_dict[message.chat.id] = user
    else:
        pass
    text_hi = "Привет!\nЯ бот, который еще нихера не умеет, но, давай знакомиться!\nКак мне тебя называть?"
    msg = bot.reply_to(message, text_hi)
    bot.register_next_step_handler(msg, acquaintanceSex)


def acquaintanceSex(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'wow buddy dat s pretty cool but I need ur NAME')
        bot.register_next_step_handler(msg, acquaintanceSex)
        return

    current_user = user_dict.get(message.chat.id)
    current_user.name = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Женский').add('Мужской').add('Я небинарное чудо')
    text_sex = "Принято, %s\nУкажите, пожалуйста, Ваш пол(sex)" % current_user.name
    msg = bot.reply_to(message, text_sex, reply_markup=keyboard)
    bot.register_next_step_handler(msg, acquaintanceHeat)


def acquaintanceHeat(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'wow buddy dat s pretty cool but I need ur SEX')
        bot.register_next_step_handler(msg, acquaintanceHeat)
        return

    current_user = user_dict.get(message.chat.id)
    sex = message.text
    if (sex == 'Женский') or (sex == 'Мужской'):
        current_user.sex = sex
    elif sex == 'Я небинарное чудо':
        text_sex2 = 'В семье не без урода. ЧТОШ....Ну а юбки и платья вы носите?'
        keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard1.add("Да", "Нет")
        msg = bot.reply_to(message, text_sex2, reply_markup=keyboard1)
        bot.register_next_step_handler(msg, acquaintanceSexAdv)
    else:
        msg = bot.reply_to(message, 'Ну и шо ты наделало, чудо?\nНормально, кнопочками пол укажи')
        bot.register_next_step_handler(msg, acquaintanceHeat)
        return

    if (current_user.sex == 'Женский') or (current_user.sex == 'Мужской'):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Я мезляч').add('Я горяч')
        msg = bot.reply_to(message, "Хорошо.\nНу тут одно из двух", reply_markup=keyboard)
        bot.register_next_step_handler(msg, acquaintanceLoc)


def acquaintanceSexAdv(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'wow buddy dat s pretty cool but I need just "yes" or "no"')
        bot.register_next_step_handler(msg, acquaintanceSexAdv)
        return

    current_user = user_dict.get(message.chat.id)
    if message.text.lower == "да":
        current_user.sex = 'Женский'
    elif message.text.lower == "нет":
        current_user.sex = 'Мужской'
    else:
        msg = bot.reply_to(message, "Просто да или нет.........")
        bot.register_next_step_handler(msg, acquaintanceSexAdv)
        return

    bot.register_next_step_handler(message, acquaintanceHeat)


def acquaintanceLoc(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'oh c\'mon just answer as if you were normal guy')
        bot.register_next_step_handler(msg, acquaintanceLoc)
        return

    if message.text != 'Я мезляч' and message.text != 'Я горяч':
        msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
        bot.register_next_step_handler(msg, acquaintanceLoc)
        return

    current_user = user_dict.get(message.chat.id)
    if message.text == 'Я мезляч' or 'Я горяч' == message.text:
        current_user.heat = True
        if message.text == 'Я горяч':
            current_user.heat = False

        text_loc = "ПРЕВОСХОДНО! А живешь ты где?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key_loc = types.KeyboardButton(text='Отправить геолокацию', request_location=True)
        keyboard.add(key_loc).add('Хочу погоду в другом городе')
        msg = bot.reply_to(message, text_loc, reply_markup=keyboard)
        bot.register_next_step_handler(msg, ProcLoc)


# @bot.message_handler(content_types=['location', 'text'])
def ProcLoc(message):
    if message.content_type != 'text' and 'location':
        msg = bot.reply_to(message, 'I need ur city or location.........pleeease')
        bot.register_next_step_handler(msg, ProcLoc)
        return

    current_user = user_dict.get(message.chat.id)
    if message.location is not None:
        try:
            current_user.loc = message.location.longitude, message.location.latitude
            # как нормально-то его обработать бля?
        except:
            bot.send_message(message.chat.id,
                             'Не могу получить Вашу геолокацию.\nВозможно,Вы закрыли Приложению доступ к ней')
    elif message.text == 'Хочу погоду в другом городе':
        txt = 'Хорошо.\nНапиши, пожалуйста, название своего города(села, деревни)\nНапример,\nМосква'
        msg = bot.reply_to(message, txt, reply_markup=None)
        bot.register_next_step_handler(msg, GeoCode)
    else:
        msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
        bot.register_next_step_handler(msg, ProcLoc)
        return


def GeoCode(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'oh c\'mon just answer as if you were normal guy')
        bot.register_next_step_handler(msg, GeoCode)
        return

    current_user = user_dict.get(message.chat.id)
    keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard1.add("Да", "Нет")
    current_user.city = message.text
    msg = bot.reply_to(message, '%s ,верно?' % current_user.city, reply_markup=keyboard1)
    bot.register_next_step_handler(msg, AdvGeoCode)


def AdvGeoCode(message):
    if message.content_type != 'text':
        msg = bot.reply_to(message, 'oh c\'mon just answer as if you were normal guy', reply_markup=None)
        bot.register_next_step_handler(msg, AdvGeoCode)
        return

    current_user = user_dict.get(message.chat.id)
    if message.text == "Да":
        list_txt = "Выберите Свой город из списка пож:"
        list_cities = keyboa_maker(items=getCoords(current_user.city))
        msg = bot.reply_to(message, list_txt, reply_markup=list_cities)
        bot.register_next_step_handler(msg, Coords)
    elif message.text == "Нет":
        msg = bot.reply_to(message, "Ну, введи еще раз))")
        bot.register_next_step_handler(msg, GeoCode, reply_markup=None)
    else:
        msg = bot.reply_to(message, "Просто да или нет.........")
        bot.register_next_step_handler(msg, AdvGeoCode)
        return


@bot.callback_query_handler(func=lambda call: bool(re.search(r"\d\d[.]\d{6}\s\d\d[.]\d{6}", call.data)))
def Coords(call):
    current_user = user_dict.get(call.from_user.id)
    current_user.loc = call.data
    bot.register_next_step_handler(call, WeatherConfigs, reply_markup=None)


def WeatherConfigs(message):
    pass


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
