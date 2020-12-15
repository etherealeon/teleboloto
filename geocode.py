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
        # todo restrict sending rivers forests ect
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        results = int(json_data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]
                      ["results"])
        found = int(
            json_data["response"]["GeoObjectCollection"]["metaDataProperty"]["GeocoderResponseMetaData"]["found"])
        num_places = min(results, found)
        address = []
        for i in range(0, num_places):
            d = {json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]
                 ["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]:
                     json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]["Point"]["pos"]}
            address.append(d)
        address.append({'Тут нет нужного города': 'Wrong city'})
        return address
    # : todo make this exc NOT 2 broad but how.........
    except Exception as e:
        return "error"
