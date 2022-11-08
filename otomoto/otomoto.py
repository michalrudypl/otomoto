import dataclasses
import datetime
import typing
import json

import requests
from bs4 import BeautifulSoup


@dataclasses.dataclass(kw_only=True)
class Car:
    vin: str
    make: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    gearbox: str
    body_type: str
    door_count: int
    nr_seats: int
    color: str
    colour_type: str = None
    country_origin: str = None
    registration: str = None
    engine_capacity: int = None
    engine_power: int = None
    version: str = None
    generation: str = None
    transmission: str = None


@dataclasses.dataclass
class Advert:
    title: str
    private_business: str
    category: str
    region: str
    subregion: str
    ad_id: int
    ad_price: int
    user_id: int
    city: str
    phone_number: int
    car: Car


class OtoMoto:
    __base_url = "https://www.otomoto.pl/"
    __phone_ajax_url = "https://www.otomoto.pl/ajax/misc/contact/all_phones/"

    def __get_phone_number(self, soup):
        seller_span = soup.find("span", class_="seller-phones__button")
        response = requests.get(
            "".join([self.__phone_ajax_url, seller_span["data-id"]])
        )
        return int(response.json()[0]["number"])

    def scrap_car_advert(self, url_or_id: typing.Union[str, int]) -> Advert:
        if not url_or_id.isdigit():
            response = requests.get(url_or_id)
        else:
            response = requests.get("".join([self.__base_url, str(url_or_id)]))

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        js_scripts = soup.find_all("script")

        for s in js_scripts:
            if "GPT.targeting" in s.text:
                advert_json = json.loads(
                    [
                        x.split("}")[0].strip()
                        for x in s.text.split("=")
                        if "title" in x
                    ][0]
                    .replace("[", "")
                    .replace("]", "")
                    + "}"
                )

        car_fields = [x.name for x in dataclasses.fields(Car)]
        advert_fields = [x.name for x in dataclasses.fields(Advert)]

        car = Car(**{k: v for k, v in advert_json.items() if k in car_fields})
        advert = Advert(
            car=car,
            **{k: v for k, v in advert_json.items() if k in advert_fields},
            phone_number=self.__get_phone_number(soup)
        )

        return advert
