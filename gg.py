import telebot
from telebot import types
from keyboa import keyboa_maker
from geocode import getCoords
from loll import Configs
import re
from users import user_dict
from telebot.types import Message
from asyncio import wait_for
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(Configs.teleboloto)


# userStep = {}   so they won't reset every time the bot restarts

isRunning: bool = False


class User:
    def __init__(self):
        self.name = ''
        self.heat = True
        self.sex = ''
        self.loc = ''
        self.city = ''
        self.rain = None
        self.car = None


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
    global isRunning
    if not isRunning:
        add_user(message.chat.id)
        text_hi = "Привет!\nЯ бот, который еще нихера не умеет, но, давай знакомиться!\nКак мне тебя называть?"
        msg = bot.reply_to(message, text_hi, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, acquaintanceSex)
        isRunning = True
    else:
        return


def acquaintanceSex(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'wow buddy dat s pretty cool but I need ur NAME', acquaintanceSex, 'text'):
            return

        current_user = user_dict.get(message.chat.id)
        current_user.name = message.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Женский').add('Мужской').add('Я небинарное чудо')
        text_sex = "Принято, %s\nУкажите, пожалуйста, Ваш пол(sex)" % current_user.name
        msg = bot.reply_to(message, text_sex, reply_markup=keyboard)
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
            keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard1.add("Да", "Нет")
            msg = bot.reply_to(message, text_sex2, reply_markup=keyboard1)
            bot.register_next_step_handler(msg, acquaintanceSexAdv)
            return

        elif sex != 'Да' and sex != 'Нет':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            msg = bot.reply_to(message, 'Ну и шо ты наделало, чудо?\nНормально, кнопочками пол укажи')
            bot.register_next_step_handler(msg, acquaintanceHeat)
            return

        if (current_user.sex == 'Женский') or (current_user.sex == 'Мужской'):
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add('Я мезляч').add('Я горяч')
            msg = bot.reply_to(message, "Хорошо.\nНу тут одно из двух", reply_markup=keyboard)
            bot.register_next_step_handler(msg, acquaintanceLoc)
            return
    else:
        to_begin(message.chat.id)


def acquaintanceSexAdv(message):

    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'wow buddy dat s pretty cool but I need just "yes" or "no"', acquaintanceSexAdv, 'text'):
            return
        if message.text.lower() == "да":
            current_user.sex = 'Женский'
        elif message.text.lower() == "нет":
            current_user.sex = 'Мужской'
        else:
            msg = bot.reply_to(message, "Просто да или нет.........")
            bot.register_next_step_handler(msg, acquaintanceSexAdv)
            return
        #bot.send_message(message.chat.id, 'Right. №5 to have trouble remembering things')
        bot.register_next_step_handler(message, acquaintanceHeat) # todo fix
        return
    else:
        to_begin(message.chat.id)


def acquaintanceLoc(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', acquaintanceLoc, 'text'):
            return

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
            try:
                current_user.loc = message.location.longitude, message.location.latitude
                return
                # todo как нормально-то его обработать бля?
            except RuntimeError:
                bot.send_message(message.chat.id,
                                 'Не могу получить Вашу геолокацию.\nВозможно,Вы закрыли Приложению доступ к ней')
        elif message.text == 'Хочу погоду в другом городе':
            txt = 'Хорошо.\nНапиши, пожалуйста, название своего города(села, деревни)\nНапример,\nМосква'
            msg = bot.reply_to(message, txt, reply_markup=None)
            bot.register_next_step_handler(msg, GeoCode)
            return

        else:
            msg = bot.reply_to(message, 'Ну кнопочками ответь, ну по-братски')
            bot.register_next_step_handler(msg, ProcLoc)
            return
    else:
        to_begin(message.chat.id)


def GeoCode(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', GeoCode, 'text'):
            return

        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard1.add("Да", "Нет")
        current_user.city = message.text
        msg = bot.reply_to(message, '%s ,верно?' % current_user.city, reply_markup=keyboard1)
        bot.register_next_step_handler(msg, AdvGeoCode)
    else:
        to_begin(message.chat.id)


def AdvGeoCode(message):
    current_user = user_dict.get(message.chat.id)
    if current_user is not None:
        if not chek(message, 'oh c\'mon just answer as if you were normal guy', AdvGeoCode, 'text'):
            return
        current_user = user_dict.get(message.chat.id)
        if message.text == "Да":
            try:
                list_txt = "Выберите Свой город из списка пож:"
                list_cities = keyboa_maker(items=getCoords(current_user.city))
                msg = bot.reply_to(message, list_txt, reply_markup=list_cities)
                bot.register_next_step_handler(msg, Coords)
            except ValueError:
                no_city_txt = 'Похоже, я не могу найти такой город\nПопробуй по-другому пож'
                msg = bot.reply_to(message, no_city_txt, reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, GeoCode)
        elif message.text == "Нет":
            msg = bot.reply_to(message, "Ну, введи еще раз))", reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, GeoCode)
            return

        else:
            msg = bot.reply_to(message, "Просто да или нет.........")
            bot.register_next_step_handler(msg, AdvGeoCode)
            return
    else:
        to_begin(message.chat.id)


@bot.callback_query_handler(func=lambda call: (bool(re.search(r"\d\d[.]\d{6}\s\d\d[.]\d{6}",
                                                              call.data))) or (call.data == 'Wrong city'))
def Coords(call):
    current_user = user_dict.get(call.from_user.id)
    if current_user is not None:
        try:
            if call.data == 'Wrong city':
                msg = bot.send_message(call.from_user.id, "Ну, введи еще раз))", reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, GeoCode)  # todo deal with these handlers
            else:
                current_user.loc = call.data
                msg = bot.send_message(call.from_user.id, "Принято",
                                       reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(msg, WeatherConfigs)

        except AttributeError:
            msg = bot.send_message(call.from_user.id, 'Пока не выберешь город из списка ничего не произойдет..')
            bot.register_next_step_handler(msg, Coords)
            return
    else:
        to_begin(call.from_user.id)


def WeatherConfigs(message: Message):
    print('gagaga')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
