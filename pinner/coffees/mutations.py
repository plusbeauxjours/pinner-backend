import graphene
from django.db import IntegrityError
from django.contrib.auth.models import User
from . import models, types
import json
from graphql_jwt.decorators import login_required
from locations import models as location_models
from locations import locationThumbnail
from notifications import models as notification_models
from django.utils import timezone


class RequestCoffee(graphene.Mutation):

    class Arguments:
        currentCityId = graphene.String(required=True)
        target = graphene.String()
        countryCode = graphene.String()
        gender = graphene.String()

    Output = types.RequestCoffeeResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        currentCityId = kwargs.get('currentCityId')
        target = kwargs.get('target', 'everyone')
        countryCode = kwargs.get('countryCode')
        gender = kwargs.get('gender')

        print("currentCityId", currentCityId)
        print("target", target)
        print("countryCode", countryCode)
        print("gender", gender)
        if not user.coffee.filter(expires__gte=timezone.now()):

            try:
                currentCity = location_models.City.objects.get(city_id=currentCityId)
                if target == "nationality" and countryCode:
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
                    if not user.profile.nationality:
                        user.profile.nationality = country
                        user.profile.save()

                elif target == "residence" and countryCode:
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
                    if not user.profile.residence:
                        user.profile.residence = country
                        user.profile.save()

                elif target == "gender" and gender:
                    user.profile.gender = gender
                    user.profile.save()
                coffee = models.Coffee.objects.create(
                    city=currentCity,
                    host=user,
                    target=target,
                )
                print(coffee)
                return types.RequestCoffeeResponse(ok=True, coffee=coffee)

            except IntegrityError as e:
                print(e)
                raise Exception("Can't create a coffee")

        else:
            raise Exception("You can't request more than one coffee")


class DeleteCoffee(graphene.Mutation):

    class Arguments:
        coffeeId = graphene.String(required=True)

    Output = types.DeleteCoffeeResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        coffeeId = kwargs.get('coffeeId')

        try:
            coffee = models.Coffee.objects.get(uuid=coffeeId)
        except models.Coffee.DoesNotExist:
            return types.DeleteCoffeeResponse(ok=False, coffeeId=None, uuid=user.profile.uuid)

        if coffee.host.id == user.id:

            coffee.delete()
            return types.DeleteCoffeeResponse(ok=True, coffeeId=coffeeId, uuid=user.profile.uuid)

        else:
            return types.DeleteCoffeeResponse(ok=False, coffeeId=None, uuid=user.profile.uuid)


class Match(graphene.Mutation):

    class Arguments:
        coffeeId = graphene.String(required=True)

    Output = types.MatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        coffeeId = kwargs.get('coffeeId')

        try:
            coffee = models.Coffee.objects.get(uuid=coffeeId)
            cityId = coffee.city.city_id
            countryCode = coffee.city.country.country_code
            continentCode = coffee.city.country.continent.continent_code
            match = models.Match.objects.create(
                host=coffee.host,
                city=coffee.city,
                guest=user,
                coffee=coffee
            )
            notification_models.Notification.objects.create(
                verb="match",
                actor=user,
                target=coffee.host,
                match=match
            )
            return types.MatchResponse(ok=True, match=match, coffeeId=coffeeId, cityId=cityId, countryCode=countryCode,
                                       continentCode=continentCode)
        except IntegrityError as e:
            print(e)
            raise Exception("Can't create a match")


class UnMatch(graphene.Mutation):

    class Arguments:
        matchId = graphene.Int(required=True)

    Output = types.UnMatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        matchId = kwargs.get('matchId')

        try:
            match = models.Match.objects.get(id=matchId)
            cityId = match.city.city_id
            countryCode = match.city.country.country_code
            continentCode = match.city.country.continent.continent_code
            match.delete()
            return types.UnMatchResponse(ok=True, matchId=matchId,  cityId=cityId, countryCode=countryCode,
                                         continentCode=continentCode)
        except models.Match.DoesNotExist:
            return types.UnMatchResponse(ok=False, matchId=None,  cityId=None, countryCode=None,
                                         continentCode=None)


class MarkAsReadMatch(graphene.Mutation):

    class Arguments:
        matchId = graphene.Int(required=True)

    Output = types.MarkAsReadMatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        matchId = kwargs.get('matchId')
        user = info.context.user

        try:
            match = models.Match.objects.get(
                id=matchId
            )
            if user == match.host:
                match.is_read_by_host = True
                match.save()
                return types.MarkAsReadMatchResponse(ok=True, matchId=matchId, isReadByHost=match.is_read_by_host, isReadByGuest=match.is_read_by_guest)
            elif user == match.guest:
                match.is_read_by_guest = True
                match.save()
                return types.MarkAsReadMatchResponse(ok=True, matchId=matchId, isReadByHost=match.is_read_by_host, isReadByGuest=match.is_read_by_guest)
            else:
                return types.MarkAsReadMatchResponse(ok=False, matchId=None, isReadByHost=None, isReadByGuest=None)

        except models.Match.DoesNotExist:
            raise Exception('This match is already unmatched ')
