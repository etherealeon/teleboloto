from pyowm.owm import OWM
import datetime
from pyowm.utils.config import get_default_config

from utils import clds, wind_converter
from loll import Configs
from clothes import clothes


def heat_config(heat, temp):
    if heat == 0:
        return temp
    elif heat == 1:
        return temp + 2
    elif heat == -1:
        return temp - 2


def precipitation_checker(code):
    if ((code >= 200) and (code <= 531)) or ((code >= 611) and (code <= 620)):
        return True
    else:
        return False


def call_owm():
    config_dict = get_default_config()
    owm = OWM(Configs.openWeather, config_dict)
    mgr = owm.weather_manager()
    return mgr


def getCurrentWeather(lat, lon):
    my_resp = call_owm().weather_at_coords(lat=lat, lon=lon)
    weather = my_resp.weather
    weathercode = clds.get(weather.weather_code)
    temp = round(weather.temperature('celsius').get('temp'))
    feels_like = round(weather.temperature('celsius').get('feels_like'))
    wind_dir = wind_converter(int(weather.wind().get('deg')))
    wind_speed = weather.wind().get('speed')
    humidity = weather.humidity
    pressure = round(weather.pressure.get('press') * 0.75006375541921)
    clouds = weather.clouds
    cityname = my_resp.location.name
    response = f'{cityname}.\nПогода сейчас: {weathercode}.\nТемпература воздуха {temp}°, ощущается как' \
               f' {feels_like}°\nВетер {wind_dir}, {wind_speed} м/c. Влажность {humidity}%. \n' \
               f'Давление {pressure} мм рт. ст. Облачность {clouds}%.'
    return response


def getTomorrowWeather(lat, lon):
    cityname = call_owm().weather_at_coords(lat=lat, lon=lon).location.name
    one_call = call_owm().one_call(lat=lat, lon=lon, exclude='minutely,hourly', units='metric')
    daily = one_call.forecast_daily[1]
    date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
    weathercode = clds.get(daily.weather_code)
    temperature_day = round(daily.temperature().get('day'))
    temperature_night = round(daily.temperature().get('night'))
    wind_dir = wind_converter(int(daily.wind().get('deg')))
    wind_speed = round(daily.wind().get('speed'))
    humidity = daily.humidity
    pressure = round(daily.pressure.get('press') * 0.75006375541921)
    clouds = daily.clouds
    response = f'{cityname}.\nПогода завтра, {date}:\n{weathercode}.\nТемпература воздуха днем: {temperature_day}°, ' \
               f'ночью: {temperature_night}°\n' \
               f'Ветер {wind_dir}, {wind_speed} м/c. Влажность {humidity}%. \n' \
               f'Давление {pressure} мм рт. ст. Облачность {clouds}%.'
    return response


def getClothNow(lat, lon, sex, heat):
    my_resp = call_owm().weather_at_coords(lat=lat, lon=lon)
    temp = round(my_resp.weather.temperature('celsius').get('feels_like'))
    weather_code = my_resp.weather.weather_code
    adapted_temp = heat_config(heat, temp)

    if precipitation_checker(weather_code):
        answ = clothes(adapted_temp, sex) + '\nТакже возможны осадки. Не забудьте зонт :)'
    else:
        answ = clothes(adapted_temp, sex)
    return answ


def getClothTomorrow(lat, lon, sex, heat):
    one_call = call_owm().one_call(lat=lat, lon=lon, exclude='minutely,hourly', units='metric')
    daily = one_call.forecast_daily[1]
    temp = round(daily.temperature().get('feels_like_day'))
    adapted_temp = heat_config(heat, temp)
    weather_code = daily.weather_code

    if precipitation_checker(weather_code):
        answ = clothes(adapted_temp, sex) + '\nТакже возможны осадки. Не забудьте зонт :)'
    else:
        answ = clothes(adapted_temp, sex)
    return answ


def hotOrCold(days, one_call):
    summ = 0
    for i in days:
        temp = one_call.forecast_daily[i].temperature().get('feels_like_day')
        summ += temp
    avg = summ / len(days)
    if avg > 23:
        return True
    else:
        return False


def getDayMin(days, one_call):
    print('there', days)
    mini = 80
    for i in days:
        fld = one_call.forecast_daily[i].temperature().get('feels_like_day')
        if fld < mini:
            mini = fld
            print(mini)
            day = i -1
    return day


def getDayMax(days, one_call):
    maxi = -80
    for i in days:
        fld = one_call.forecast_daily[i].temperature().get('feels_like_day')
        if fld > maxi:
            maxi = fld
            print(maxi)
            day = i -1
    return day


def bestDay(lat, lon):
    days = [1, 2, 3, 4, 5, 6]
    one_call = call_owm().one_call(lat=lat, lon=lon, exclude='minutely,hourly', units='metric')
    for i in days:
        weather_code = one_call.forecast_daily[i].weather_code
        if precipitation_checker(weather_code):
            days.remove(i)
    if len(days) == 1:
        daily = one_call.forecast_daily[days[0]]
        date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
        return f'Наилучший день для прогулки: {date}.\nОсадков не ожидается.'
    elif len(days) == 0:
        days = [1, 2, 3, 4, 5, 6]
        if hotOrCold(days, one_call):
            day = getDayMin(days, one_call)
            daily = one_call.forecast_daily[days[day]]
            date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
            f'Наилучший день для прогулки: {date}.\n Но в этот день ожидаются осадки, возьмите зонт)'
        else:
            day = getDayMax(days, one_call)
            daily = one_call.forecast_daily[days[day]]
            date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
            f'Наилучший день для прогулки: {date}.\n Но в этот день ожидаются осадки, возьмите зонт)'

    else:
        print('ax', len(days))
        print('here' ,days)
        if hotOrCold(days, one_call):
            day = getDayMin(days, one_call)
            daily = one_call.forecast_daily[days[day]]
            date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
            return f'Наилучший день для прогулки: {date}.\nОсадков не ожидается.'
        else:
            day = getDayMax(days, one_call)
            daily = one_call.forecast_daily[days[day]]
            date = datetime.datetime.fromtimestamp(daily.ref_time).strftime('%d.%m')
            return f'Наилучший день для прогулки: {date}.\nОсадков не ожидается.'


