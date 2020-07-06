import uuid
import json
import random
from django.core.management.base import BaseCommand
from locations import models as location_models
from locations import locationThumbnail


class Command(BaseCommand):

    help = "It seeds the DB with tons of stuff"

    def handle(self, *args, **options):

        # CREATE CITY

        all_countries = location_models.Country.objects.all()
        for i in all_countries:
            if i.countryPhotoURL == None or i.countryThumbnailURL == None:
                try:
                    gp = locationThumbnail.get_photos(term=i.countryName).get_urls()
                    countryPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
                    countryThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
                except:
                    countryPhotoURL = None
                    countryThumbnailURL = None

                i.country_photo = countryPhotoURL,
                i.country_thumbnail = countryThumbnailURL
                i.save()
                print(i.country_name)

        all_cities = location_models.City.objects.all()
        for i in all_cities:
            if i.cityPhotoURL == None or i.cityThumbnailURL == None:
                try:
                    gp = locationThumbnail.get_photos(term=i.cityName).get_urls()
                    cityPhotoURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=450&w=450&fit=crop"
                    cityThumbnailURL = gp+"?ixlib=rb-0.3.5&q=100&fm=jpg&crop=entropy&cs=faces&h=80&w=80&fit=crop"
                except:
                    cityPhotoURL = None
                    cityThumbnailURL = None

                i.city_photo = cityPhotoURL,
                i.city_thumbnail = cityThumbnailURL
                i.save()
                print(i.city_name)

        self.stdout.write(self.style.SUCCESS(f"Everything seeded"))
