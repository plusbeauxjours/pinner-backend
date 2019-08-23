import graphene
import json
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required

from . import models, types
from . import locationThumbnail
from . import reversePlace
from notifications import models as notification_models

from utils import notify_slack


class CreateCity(graphene.Mutation):

    class Arguments:
        cityId = graphene.String(required=True)

    Output = types.CreateCityResponse

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user

        cityId = kwargs.get('cityId')

        def get_locations_nearby_coords(latitude, longitude, max_distance=3000):
            gcd_formula = "6371 * acos(cos(radians(%s)) * \
            cos(radians(latitude)) \
            * cos(radians(longitude) - radians(%s)) + \
            sin(radians(%s)) * sin(radians(latitude)))"
            distance_raw_sql = RawSQL(
                gcd_formula,
                (latitude, longitude, latitude)
            )
            qs = models.City.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
            if max_distance is not None:
                qs = qs.filter(distance__lt=max_distance)
                for i in qs:
                    pass
                return qs

        try:
            city = models.City.objects.get(city_id=cityId)
            return types.CreateCityResponse(ok=True)
        except models.City.DoesNotExist:
            cityLatitude, cityLongitude, cityName, countryCode = reversePlace.reverse_place(cityId)
            nearCities = get_locations_nearby_coords(cityLatitude, cityLongitude, 3000)[:20]

            try:
                country = models.Country.objects.get(country_code=countryCode)
            except models.Country.DoesNotExist:

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
                        continent = models.Continent.objects.get(continent_code=continentCode)
                    except:
                        with open('pinner/locations/continentData.json', mode='rt', encoding='utf-8') as file:
                            continentData = json.load(file)
                            continentName = continentData[continentCode]

                            try:
                                gp = locationThumbnail.get_photos(term=continentName)
                                continentPhotoURL = gp.get_urls()
                            except:
                                continentPhotoURL = None

                            continent = models.Continent.objects.create(
                                continent_name=continentName,
                                continent_photo=continentPhotoURL,
                                continent_code=continentCode
                            )
                try:
                    gp = locationThumbnail.get_photos(term=countryName)
                    countryPhotoURL = gp.get_urls()
                except:
                    countryPhotoURL = None
                country = models.Country.objects.create(
                    country_code=countryCode,
                    country_name=countryName,
                    country_name_native=countryNameNative,
                    country_capital=countryCapital,
                    country_currency=countryCurrency,
                    country_phone=countryPhone,
                    country_emoji=countryEmoji,
                    country_photo=countryPhotoURL,
                    continent=continent,
                    latitude=latitude,
                    longitude=longitude
                )

            try:
                gp = locationThumbnail.get_photos(term=cityName)
                cityPhotoURL = gp.get_urls()
            except:
                cityPhotoURL = None
            city = models.City.objects.create(
                city_id=cityId,
                city_name=cityName,
                country=country,
                city_photo=cityPhotoURL,
                latitude=cityLatitude,
                longitude=cityLongitude
            )
            for i in nearCities:
                city.near_city.add(i)
                city.save()

        return types.CreateCityResponse(ok=True)


class ReportLocation(graphene.Mutation):

    class Arguments:
        currentLat = graphene.Float(required=True)
        currentLng = graphene.Float(required=True)
        currentCityId = graphene.String()
        currentCityName = graphene.String(required=True)
        currentCountryCode = graphene.String(required=True)

    Output = types.ReportLocationResponse

    def mutate(self, info, **kwargs):
        user = info.context.user
        profile = user.profile

        currentLat = kwargs.get('currentLat')
        currentLng = kwargs.get('currentLng')
        currentCityId = kwargs.get('currentCityId')
        currentCityName = kwargs.get('currentCityName')
        currentCountryCode = kwargs.get('currentCountryCode')

        def get_locations_nearby_coords(latitude, longitude, max_distance=3000):
            gcd_formula = "6371 * acos(cos(radians(%s)) * \
            cos(radians(latitude)) \
            * cos(radians(longitude) - radians(%s)) + \
            sin(radians(%s)) * sin(radians(latitude)))"
            distance_raw_sql = RawSQL(
                gcd_formula,
                (latitude, longitude, latitude)
            )
            qs = models.City.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
            if max_distance is not None:
                qs = qs.filter(Q(distance__lt=max_distance))
                for i in qs:
                    pass
            return qs

        try:
            country = models.Country.objects.get(country_code=currentCountryCode)
            with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
                countryData = json.load(file)
                currentCountry = countryData[currentCountryCode]
                continentCode = currentCountry['continent']
                continent = models.Continent.objects.get(continent_code=continentCode)

        except models.Country.DoesNotExist:
            with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
                countryData = json.load(file)
                currentCountry = countryData[currentCountryCode]
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
                    continent = models.Continent.objects.get(continent_code=continentCode)
                except:
                    with open('pinner/locations/continentData.json', mode='rt', encoding='utf-8') as file:
                        continentData = json.load(file)
                        continentName = continentData[continentCode]

                        try:
                            gp = locationThumbnail.get_photos(term=continentName)
                            continentPhotoURL = gp.get_urls()
                        except:
                            continentPhotoURL = None

                        continent = models.Continent.objects.create(
                            continent_name=continentName,
                            continent_photo=continentPhotoURL,
                            continent_code=continentCode
                        )
            try:
                gp = locationThumbnail.get_photos(term=countryName)
                countryPhotoURL = gp.get_urls()
            except:
                countryPhotoURL = None

            country = models.Country.objects.create(
                country_code=currentCountryCode,
                country_name=countryName,
                country_name_native=countryNameNative,
                country_capital=countryCapital,
                country_currency=countryCurrency,
                country_phone=countryPhone,
                country_emoji=countryEmoji,
                country_photo=countryPhotoURL,
                continent=continent,
                latitude=latitude,
                longitude=longitude
            )

        try:
            city = models.City.objects.get(city_id=currentCityId)
            profile.current_city = city
            profile.current_country = city.country
            profile.current_continent = city.country.continent
            profile.save()
            if city.near_city.count() < 20:
                nearCities = get_locations_nearby_coords(currentLat, currentLng, 3000)[:20]
                for i in nearCities:
                    city.near_city.add(i)
                    city.save()

        except models.City.DoesNotExist:
            nearCities = get_locations_nearby_coords(currentLat, currentLng, 3000)[:20]

            try:
                gp = locationThumbnail.get_photos(term=currentCityName)
                cityPhotoURL = gp.get_urls()
            except:
                cityPhotoURL = None

            city = models.City.objects.create(
                city_id=currentCityId,
                city_name=currentCityName,
                country=country,
                city_photo=cityPhotoURL,
                latitude=currentLat,
                longitude=currentLng
            )
            for i in nearCities:
                city.near_city.add(i)
                city.save()
            profile.current_city = city
            profile.current_country = city.country
            profile.current_continent = city.country.continent
            profile.save()
            return city

        if profile.is_auto_location_report is True:
            try:
                latest = user.moveNotificationUser.latest('start_date', 'created_at')
                if latest.city != city:
                    notification_models.MoveNotification.objects.create(
                        actor=user, city=city, country=country, continent=continent)
                    return types.ReportLocationResponse(ok=True)
            except notification_models.MoveNotification.DoesNotExist:
                notification_models.MoveNotification.objects.create(
                    actor=user, city=city, country=country, continent=continent)
                return types.ReportLocationResponse(ok=True)

        return types.ReportLocationResponse(ok=True)


class ToggleLikeCity(graphene.Mutation):

    """ Like a City """

    class Arguments:
        cityId = graphene.Int(required=True)

    Output = types.ToggleLikeCityResponse

    @login_required
    def mutate(self, info, **kwargs):

        cityId = kwargs.get('cityId')
        user = info.context.user

        try:
            city = models.City.objects.get(id=cityId)
        except models.City.DoesNotExist:
            raise Exception("City Not Found")

        try:
            like = models.Like.objects.get(
                creator=user, city=city)
            like.delete()
            return types.ToggleLikeCityResponse(ok=True, city=city)

        except models.Like.DoesNotExist:
            pass

        try:
            like = models.Like.objects.create(
                creator=user, city=city)
            return types.ToggleLikeCityResponse(ok=True, city=city)

        except IntegrityError as e:
            raise Exception("Can't Like City")


class SlackReportLocation(graphene.Mutation):

    class Arguments:
        targetLocationId = graphene.String(required=True)
        targetLocationType = graphene.String(required=True)
        payload = graphene.String(required=True)

    Output = types.SlackReportLocationResponse

    def mutate(self, info, **kwargs):

        reportUsername = info.context.user.username
        targetLocationId = kwargs.get('targetLocationId')
        targetLocationType = kwargs.get('targetLocationType')
        payload = kwargs.get('payload')

        if payload == "PHOTO":
            if targetLocationType == "city":
                city = models.City.objects.get(city_id=targetLocationId)
                to_channel = "#location_%s_reports" % (city.country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported city: %s" % (city.city_name),
                    "title_link": "http://localhost:3000/city/%s" % (city.city_id),
                    "text": "%s reports that %s has inappropriate PHOTO" % (reportUsername, city.city_name),
                    "image_url": city.city_photo,
                    "footer": "🙅🏻‍♂️ Inappropriate Photo!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            elif targetLocationType == "country":
                country = models.Country.objects.get(country_code=targetLocationId)
                to_channel = "#location_%s_reports" % (country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported country: %s %s" % (country.country_name, country.country_emoji),
                    "title_link": "http://localhost:3000/country/%s" % (country.country_code),
                    "text": "%s reports that %s %s has inappropriate PHOTO" % (reportUsername, country.country_name, country.country_emoji),
                    "image_url": country.country_photo,
                    "footer": "🙅🏻‍♂️ Inappropriate Photo!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)

            elif targetLocationType == "continent":
                continent = models.Continent.objects.get(continent_code=targetLocationId)
                to_channel = "#location_%s_reports" % (continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported continent: %s" % (continent.continent_name),
                    "title_link": "http://localhost:3000/continent/%s" % (continent.continent_code),
                    "text": "%s reports that %s has inappropriate PHOTO" % (reportUsername, continent.continent_name),
                    "image_url": continent.continent_photo,
                    "footer": "🙅🏻‍♂️ Inappropriate Photo!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            else:
                return types.SlackReportLocationResponse(ok=False)
        elif(payload == "LOCATION"):
            if targetLocationType == "city":
                city = models.City.objects.get(city_id=targetLocationId)
                to_channel = "#location_%s_reports" % (city.country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported city: %s" % (city.city_name),
                    "title_link": "http://localhost:3000/city/%s" % (city.city_id),
                    "text": "%s reports that %s has wrong LOCATION" % (reportUsername, city.city_name),
                    "image_url": city.city_photo,
                    "footer": "🤦🏻‍♂️ Wrong Location!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            elif targetLocationType == "country":
                country = models.Country.objects.get(country_code=targetLocationId)
                to_channel = "#location_%s_reports" % (country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported country: %s %s" % (country.country_name, country.country_emoji),
                    "title_link": "http://localhost:3000/country/%s" % (country.country_code),
                    "text": "%s reports that %s %s haswrong LOCATION" % (reportUsername, country.country_name, country.country_emoji),
                    "image_url": country.country_photo,
                    "footer": "🤦🏻‍♂️ Wrong Location!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)

            elif targetLocationType == "continent":
                continent = models.Continent.objects.get(continent_code=targetLocationId)
                to_channel = "#location_%s_reports" % (continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported continent: %s" % (continent.continent_name),
                    "title_link": "http://localhost:3000/continent/%s" % (continent.continent_code),
                    "text": "%s reports that %s has wrong LOCATION" % (reportUsername, continent.continent_name),
                    "image_url": continent.continent_photo,
                    "footer": "🤦🏻‍♂️ Wrong Location!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            else:
                return types.SlackReportLocationResponse(ok=False)
        elif(payload == "OTHER"):
            if targetLocationType == "city":
                city = models.City.objects.get(city_id=targetLocationId)
                to_channel = "#location_%s_reports" % (city.country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported city: %s" % (city.city_name),
                    "title_link": "http://localhost:3000/city/%s" % (city.city_id),
                    "text": "%s reports %s" % (reportUsername, city.city_name),
                    "image_url": city.city_photo,
                    "footer": "🤦🏻‍♂️ Other Report!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            elif targetLocationType == "country":
                country = models.Country.objects.get(country_code=targetLocationId)
                to_channel = "#location_%s_reports" % (country.continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported country: %s %s" % (country.country_name, country.country_emoji),
                    "title_link": "http://localhost:3000/country/%s" % (country.country_code),
                    "text": "%s reports %s %s" % (reportUsername, country.country_name, country.country_emoji),
                    "image_url": country.country_photo,
                    "footer": "🤦🏻‍♂️ Other Report!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)

            elif targetLocationType == "continent":
                continent = models.Continent.objects.get(continent_code=targetLocationId)
                to_channel = "#location_%s_reports" % (continent.continent_code.lower())
                attachments = [{
                    "fallback": "Required plain-text summary of the attachment.",
                    "color": "#80318c",
                    # "pretext": "Optional text that appears above the attachment block",
                    "author_name": reportUsername,
                    "author_link": "http://localhost:3000/%s" % (reportUsername),
                    "title":  "reported continent: %s" % (continent.continent_name),
                    "title_link": "http://localhost:3000/continent/%s" % (continent.continent_code),
                    "text": "%s reports %s" % (reportUsername, continent.continent_name),
                    "image_url": continent.continent_photo,
                    "footer": "🤦🏻‍♂️ Other Report!"
                }]
                notify_slack(to_channel, attachments)
                return types.SlackReportLocationResponse(ok=True)
            else:
                return types.SlackReportLocationResponse(ok=False)
