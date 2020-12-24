import requests
from loll import Configs


def getCoords(city):
    PARAMS = {
        "apikey": Configs.yan,
        "format": "json",
        "lang": "ru_RU",
        "kind": "locality",
        "geocode": city
    }
    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        results = int(json_data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]
                      ["results"])
        found = int(
            json_data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]["found"])
        num_places = min(results, found)
        address = []
        for i in range(0, num_places):
            kind = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"
                ]['metaDataProperty']['GeocoderMetaData']['kind']
            if kind == 'locality' or kind == "province" or kind == "district" or kind == "area":
                place_name = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]["name"]
                place_d = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]["description"]
                loc = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]["Point"]["pos"]
                d = {place_name + ', '+ place_d: loc}
                address.append(d)
        address.append({'Тут нет нужного города': 'Wrong city'})
        return address
    except KeyError as e:
        return e

