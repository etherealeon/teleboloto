from pyowm.owm import OWM
from loll import Configs
from pyowm.utils.config import get_default_config
from utils import clds, wind_converter


# C:\Users\я\PycharmProjects\LES2\venv\Lib\site-packages\pyowm\weatherapi25
def getCurrentWeather(lat, lon):
    config_dict = get_default_config()
    owm = OWM(Configs.openWeather, config_dict)
    mgr = owm.weather_manager()
    my_resp = mgr.weather_at_coords(lat=lat, lon=lon)
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
    responce = f'{cityname}. Погода сейчас: {weathercode}.\nТемпература воздуха {temp}°,ощущается как' \
               f' {feels_like}°\nВетер {wind_dir}, {wind_speed} м/c. Влажность {humidity}%. \n' \
               f'Давление {pressure} мм рт. ст. Облачность {clouds}%.'
    return responce


def getTomorrowWeather(lat, lon):
    config_dict = get_default_config()
    owm = OWM(Configs.openWeather, config_dict)
    mgr = owm.weather_manager()
    cityname = mgr.weather_at_coords(lat=lat, lon=lon).location.name
    one_call = mgr.one_call(lat=lat, lon=lon, exclude='minutely,hourly', units='metric')
    weather = one_call.location(lat=lat, lon=lon)
    pop = one_call.forecast_daily[1].__dict__
    print(pop)
    date = weather.reference_time('date')
    weathercode = weather.weather_code
    temperature = one_call.forecast_daily[1].temperature()
    #  todo choose how to show temp
    # temp = round(weather.temperature('celsius').get('temp'))
    # feels_like = round(weather.temperature('celsius').get('feels_like'))
    wind_dir = wind_converter(int(weather.wind().get('deg')))
    wind_speed = weather.wind().get('speed')
    humidity = weather.humidity
    pressure = round(weather.pressure.get('press') * 0.75006375541921)
    clouds = weather.clouds
    return # todo make a return


getCurrentWeather(55.75222, 37.617635)
