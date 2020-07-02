import uuid
import json
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from users import models as user_models
from locations import models as location_models
from django_seed import Seed
from django.db.models.expressions import RawSQL
from locations import reversePlace, locationThumbnail


def createCity(cityId):
    def get_locations_nearby_coords(latitude, longitude, max_distance=3000):
        gcd_formula = "6371 * acos(cos(radians(%s)) * \
        cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)))"
        distance_raw_sql = RawSQL(
            gcd_formula,
            (latitude, longitude, latitude)
        )
        qs = location_models.City.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
        if max_distance is not None:
            qs = qs.filter(distance__lt=max_distance)
            for i in qs:
                pass
            return qs

    cityLatitude, cityLongitude, cityName, countryCode = reversePlace.reverse_place(cityId)
    nearCities = get_locations_nearby_coords(cityLatitude, cityLongitude, 3000)[:20]

    try:
        country = location_models.Country.objects.get(country_code=countryCode)
    except location_models.Country.DoesNotExist:

        with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
            countryData = json.load(file)
            currentCountry = countryData[countryCode]
            countryName = currentCountry['name']
            countryNameNative = currentCountry['native']
            countryCapital = currentCountry['capital']
            countryCurrency = currentCountry['currency']
            countryPhone = currentCountry['phone']
            countryEmoji = currentCountry['emoji']
            continentCode = currentCountry['continent']
            latitude = currentCountry['latitude']
            longitude = currentCountry['longitude']

            try:
                continent = location_models.Continent.objects.get(continent_code=continentCode)
            except:
                with open('pinner/locations/continentData.json', mode='rt', encoding='utf-8') as file:
                    continentData = json.load(file)
                    continentName = continentData[continentCode]

                    try:
                        gp = locationThumbnail.get_photos(term=continentName).get_urls()
                        continentPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
                        continentThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
                    except:
                        continentPhotoURL = None
                        continentThumbnailURL = None

                    continent = location_models.Continent.objects.create(
                        continent_name=continentName,
                        continent_photo=continentPhotoURL,
                        continent_thumbnail=continentThumbnailURL,
                        continent_code=continentCode
                    )
        try:
            gp = locationThumbnail.get_photos(term=countryName).get_urls()
            countryPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
            countryThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
        except:
            countryPhotoURL = None
            countryThumbnailURL = None
        country = location_models.Country.objects.create(
            country_code=countryCode,
            country_name=countryName,
            country_name_native=countryNameNative,
            country_capital=countryCapital,
            country_currency=countryCurrency,
            country_phone=countryPhone,
            country_emoji=countryEmoji,
            country_photo=countryPhotoURL,
            country_thumbnail=countryThumbnailURL,
            continent=continent,
            latitude=latitude,
            longitude=longitude
        )

    try:
        gp = locationThumbnail.get_photos(term=cityName).get_urls()
        cityPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
        cityThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
    except:
        cityPhotoURL = None
        cityThumbnailURL = None
    city = location_models.City.objects.create(
        city_id=cityId,
        city_name=cityName,
        country=country,
        city_photo=cityPhotoURL,
        city_thumbnail=cityThumbnailURL,
        latitude=cityLatitude,
        longitude=cityLongitude
    )
    for i in nearCities:
        city.near_city.add(i)
        city.save()


cityIds = [
    "ChIJXW-7kH462jARZ0ObpXBi1Jg"
]


class Command(BaseCommand):

    help = "It seeds the DB with tons of stuff"

    def handle(self, *args, **options):
        # for i in cityIds:
        #     createCity(i)

        # user_seeder = Seed.seeder()
        # user_seeder.add_entity(
        #     user_models.User,
        #     10,
        #     {
        #         "uuid": lambda x: uuid.uuid4(),
        #         "residence": None,
        #         "nationality": None,
        #         "is_staff": False,
        #         "is_superuser": False,
        #         "current_city": None,
        #         "current_country": None,
        #         "current_continent": None,
        #     },
        # )
        # user_seeder.execute()

        self.stdout.write(self.style.SUCCESS(f"Everything seeded"))
