import requests
from loll import Configs


# "hydro" "area" "airport" "railway_station" "district" "street"
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
            kind = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"
                ]['metaDataProperty']['GeocoderMetaData']['kind']
            if kind != 'hydro':
                place_text = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"
                ]["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]

                loc = json_data["response"]["GeoObjectCollection"]["featureMember"][i]["GeoObject"]["Point"]["pos"]
                d = {place_text: loc}
                address.append(d)
        address.append({'Тут нет нужного города': 'Wrong city'})
        return address
    except KeyError as e:
        return e


print(getCoords('Кисегач'))
