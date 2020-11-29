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
    # rain = weather.rain
    # snow = weather.snow
    clouds = weather.clouds
    cityname = my_resp.location.name
    # ref_time = weather.reference_time(timeformat='date')
    responce = f'{cityname}. Погода сейчас: {weathercode}.\nТемпература воздуха {temp}°,ощущается как' \
               f' {feels_like}°\nВетер {wind_dir}, {wind_speed} м/c. Влажность {humidity}%. \n' \
               f'Давление {pressure} мм рт. ст. Облачность {clouds}%.'
    return responce


x = getCurrentWeather(55.75222, 37.617635)
# print(x)
config_dict = get_default_config()
owm = OWM(Configs.openWeather, config_dict)
mgr = owm.weather_manager()
one_call = mgr.one_call(lat=55.75222, lon=37.617635, units='metric')
print(one_call.forecast_daily[0].__dict__)
weathercode = one_call.forecast_daily[0].weather_code
utc_offset = one_call.forecast_daily[0]
rain = one_call.current.rain
snow = one_call.current.snow
wind = one_call.current.wind()
temperature = one_call.forecast_daily[0].temperature()
clouds = one_call.current.clouds
pressure = one_call.current.pressure
humidity = one_call.current.humidity
print(temperature)