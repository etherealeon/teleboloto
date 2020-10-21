import telebot
from telebot import types
from keyboa import keyboa_maker
from geocode import getCoords
from loll import Configs

bot = telebot.TeleBot(Configs.teleboloto)
user_dict = {}


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
    text_hi = "Привет!\nЯ бот, который еще нихера не умеет, но, давай знакомиться!\nКак мне тебя называть?"
    msg = bot.reply_to(message, text_hi)
    bot.register_next_step_handler(msg, acquaintanceSex)


# @bot.message_handler
def acquaintanceSex(message):
    ouruser = User()
    ouruser.name = message.text
    user_dict[message.chat.id] = ouruser
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    key_female = types.KeyboardButton(text='Женский')  # кнопка «Да»
    key_male = types.KeyboardButton(text='Мужской')
    key_nonbinary = types.KeyboardButton(text='Я небинарное чудо')
    keyboard.add(key_nonbinary).add(key_male).add(key_female)
    text_sex = "Принято, %s\nУкажите, пожалуйста, Ваш пол(sex)" % ouruser.name
    msg = bot.reply_to(message, text_sex, reply_markup=keyboard)
    bot.register_next_step_handler(msg, acquaintanceHeat)


def acquaintanceHeat(message,):
    user = user_dict[message.chat.id]
    sex = message.text
    if (sex == 'Женский') or (sex == 'Мужской'):
        user.sex = sex
    elif sex == 'Я небинарное чудо':
        text_sex2 = 'В семье не без урода. ЧТОШ....Ну а юбки и платья вы носите?'
        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard1.add("Да", "Нет")
        msg = bot.reply_to(message, text_sex2, reply_markup=keyboard1)
        bot.register_next_step_handler(msg, acquaintanceSexAdv)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
    if (user.sex == 'Женский') or (user.sex == 'Мужской'):
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        key_hot = types.KeyboardButton(text='Я мезляч')
        key_cold = types.KeyboardButton(text='Я горяч')
        keyboard.add(key_hot).add(key_cold)
        msg = bot.reply_to(message, "Хорошо.\nНу тут одно из двух", reply_markup=keyboard)
        bot.register_next_step_handler(msg, acquaintanceLoc)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def acquaintanceSexAdv(message):
    user = user_dict[message.chat.id]
    if message.text == "Да":
        user.sex = 'Женский'
    elif message.text == "Нет":
        user.sex = 'Мужской'
    else:
        pass
    bot.register_next_step_handler(message, acquaintanceHeat)


def acquaintanceLoc(message):
    user = user_dict[message.chat.id]
    if message.text == 'Я мезляч':
        user.heat = True
    elif message.text == 'Я горяч':
        user.heat = False
    else:
        pass
    text_loc = "ПРЕВОСХОДНО! А живешь ты где?"
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    key_loc = types.KeyboardButton(text='Отправить геолокацию', request_location=True)
    key_txt = types.KeyboardButton(text='Хочу погоду в другом городе')
    keyboard.add(key_loc).add(key_txt)
    msg = bot.reply_to(message, text_loc, reply_markup=keyboard)
    bot.register_next_step_handler(msg, ProcLoc)


@bot.message_handler(content_types=['location', 'text'])
def ProcLoc(message):
    if message.location is not None:
        try:
            print(message.location)
            print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))
            # как нормально-то его обработать бля?
        except:
            bot.send_message(message.chat.id,
                             'Не могу получить Вашу геолокацию.\nВозможно,Вы закрыли Приложению доступ к ней U+1F609')
    elif message.text == 'Хочу погоду в другом городе':
        txt = "Хорошо.\nНапиши, пожалуйста, название своего города(села, деревни)\nНапример,\nМосква"
        msg = bot.reply_to(message, txt)
        bot.register_next_step_handler(msg, GeoCode)


def GeoCode(message):
    user = user_dict[message.chat.id]
    keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard1.add("Да", "Нет")
    user.city = message.text
    msg = bot.reply_to(message, '%s ,верно?' % user.city, reply_markup=keyboard1)
    bot.register_next_step_handler(msg, AdvGeoCode)


def AdvGeoCode(message):
    user = user_dict[message.chat.id]
    if message.text == "Да":
        list_txt = "Выберите Свой город из списка пож:"
        list_cities = keyboa_maker(items=getCoords(user.city))
        msg = bot.reply_to(message, list_txt, reply_markup=list_cities)
        bot.register_next_step_handler(msg, Coords)
    elif message.text == "Нет":
        msg = bot.reply_to(message, "Ну, введи еще раз))")
        bot.register_next_step_handler(msg, GeoCode, reply_markup=None)
    else:
        pass


def Coords(message):
    pass


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
