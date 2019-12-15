import random
import math
import json

import graphene
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from graphene_file_upload.scalars import Upload

from django.db.models.expressions import RawSQL
from locations import locationThumbnail
from locations import reversePlace
from locations import models as location_models
from . import models, types

from utils import notify_slack
from notifications import models as notification_models

from django.core.files.base import ContentFile
from io import BytesIO
from urllib.request import urlopen


class ToggleSettings(graphene.Mutation):

    class Arguments:
        payload = graphene.String(required=True)

    Output = types.ToggleSettingsResponse

    @login_required
    def mutate(self, info,  **kwargs):

        user = info.context.user
        payload = kwargs.get('payload')
        print("0",payload)
        if payload == "DARK_MODE":
            if user.profile.is_dark_mode == True:
                try:
                    user.profile.is_dark_mode = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_dark_mode == False:
                try:
                    user.profile.is_dark_mode = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_PHOTOS":
            if user.profile.is_hide_photos == True:
                try:
                    print("1.1",user.profile.is_hide_photos)
                    user.profile.is_hide_photos = False
                    user.profile.save()
                    print("1.1",user.profile.is_hide_photos)
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    print("2",user.profile.is_hide_photos)
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_photos == False:
                try:
                    print("3.1",user.profile.is_hide_photos)
                    user.profile.is_hide_photos = True
                    user.profile.save()
                    print("3.2",user.profile.is_hide_photos)
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    print("4",user.profile.is_hide_photos)
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_TRIPS":
            if user.profile.is_hide_trips == True:
                try:
                    user.profile.is_hide_trips = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_trips == False:
                try:
                    user.profile.is_hide_trips = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_COFFEES":
            if user.profile.is_hide_coffees == True:
                try:
                    user.profile.is_hide_coffees = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_coffees == False:
                try:
                    user.profile.is_hide_coffees = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)

        elif payload == "HIDE_CITIES":
            if user.profile.is_hide_cities == True:
                try:
                    user.profile.is_hide_cities = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_cities == False:
                try:
                    user.profile.is_hide_cities = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_COUNTRIES":
            if user.profile.is_hide_countries == True:
                try:
                    user.profile.is_hide_countries = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_countries == False:
                try:
                    user.profile.is_hide_countries = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_CONTINENTS":
            if user.profile.is_hide_continents == True:
                try:
                    user.profile.is_hide_continents = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_hide_continents == False:
                try:
                    user.profile.is_hide_continents = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "AUTO_LOCATION_REPORT":
            if user.profile.is_auto_location_report == True:
                try:
                    user.profile.is_auto_location_report = False
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.profile.is_auto_location_report == False:
                try:
                    user.profile.is_auto_location_report = True
                    user.profile.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)


class EditProfile(graphene.Mutation):

    class Arguments:
        username = graphene.String()
        bio = graphene.String()
        gender = graphene.String()
        firstName = graphene.String()
        lastName = graphene.String()
        nationalityCode = graphene.String()
        residenceCode = graphene.String()

    Output = types.EditProfileResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        profile = user.profile

        if user.is_authenticated and profile is not None:

            bio = kwargs.get('bio', user.profile.bio)
            gender = kwargs.get('gender', user.profile.gender)
            firstName = kwargs.get('firstName', user.first_name)
            lastName = kwargs.get('lastName', user.last_name)
            username = kwargs.get('username', user.username)
            nationalityCode = kwargs.get('nationalityCode', user.profile.nationality)
            residenceCode = kwargs.get('residenceCode', user.profile.residence)

            # if username:
            #     raise Exception("Only English username is allowed "

            try:
                nationality = location_models.Country.objects.get(country_code=nationalityCode)
            except location_models.Country.DoesNotExist:
                with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
                    countryData = json.load(file)
                    currentCountry = countryData[nationalityCode]
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

                            # DOWNLOAD IMAGE
                            # continentPhotoURL = gp.get_urls()
                            # # for i in range(gp.num):
                            # #     gp.download(i)

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

                # DOWNLOAD IMAGE
                # for i in range(gp.num):
                #     gp.download(i)

                nationality = location_models.Country.objects.create(
                    country_code=nationalityCode,
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
                residence = location_models.Country.objects.get(country_code=residenceCode)
            except location_models.Country.DoesNotExist:
                with open('pinner/locations/countryData.json', mode='rt', encoding='utf-8') as file:
                    countryData = json.load(file)
                    currentCountry = countryData[residenceCode]
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

                            # DOWNLOAD IMAGE
                            # continentPhotoURL = gp.get_urls()
                            # # for i in range(gp.num):
                            # #     gp.download(i)

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

                # DOWNLOAD IMAGE
                # for i in range(gp.num):
                #     gp.download(i)

                residence = location_models.Country.objects.create(
                    country_code=residenceCode,
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
                profile.bio = bio
                profile.gender = gender
                profile.nationality = nationality
                profile.residence = residence
                profile.save()

                user.first_name = firstName
                user.last_name = lastName
                if user.username != username:
                    try:
                        existing_user = User.objects.get(username=username)
                        raise Exception("Username is already taken")
                    except User.DoesNotExist:
                        user.username = username
                user.save()
                token = get_token(user)
                return types.EditProfileResponse(ok=True, user=user, token=token)

            except IntegrityError as e:
                print(e)
                error = "Can't save"
                return types.EditProfileResponse(ok=False, user=None, token=None)

        else:
            error = 'You need to log in'
            return types.EditProfileResponse(ok=False, user=None, token=None)


class MarkAsMain(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    Output = types.MarkAsMainResponse

    @login_required
    def mutate(self, info,  **kwargs):

        user = info.context.user
        uuid = kwargs.get('uuid')

        try:
            prevMainAvatar = models.Avatar.objects.get(
                is_main=True, creator=user)
            if prevMainAvatar:
                newMainAvatar = models.Avatar.objects.get(uuid=uuid)
                prevMainAvatar.is_main = False
                newMainAvatar.is_main = True
                user.profile.avatar_url = newMainAvatar.thumbnail
                user.profile.app_avatar_url = newMainAvatar.app_thumbnail
                user.profile.save()
                prevMainAvatar.save()
                newMainAvatar.save()
                return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar,  preAvatarUUID=prevMainAvatar.uuid, newAvatarUUID=uuid)
            else:
                newMainAvatar = models.Avatar.objects.get(uuid=uuid)
                newMainAvatar.is_main = True
                user.profile.avatar_url = newMainAvatar.thumbnail
                user.profile.app_avatar_url = newMainAvatar.app_thumbnail
                user.profile.save()
                newMainAvatar.save()
                return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar,  preAvatarUUID=None, newAvatarUUID=uuid)

        except models.Avatar.DoesNotExist:
            newMainAvatar = models.Avatar.objects.get(uuid=uuid)
            newMainAvatar.is_main = True
            user.profile.avatar_url = newMainAvatar.thumbnail
            user.profile.app_avatar_url = newMainAvatar.app_thumbnail
            user.profile.save()
            newMainAvatar.save()
            return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar, preAvatarUUID=None, newAvatarUUID=uuid)

class  RegisterPush(graphene.Mutation):

    class Arguments:
        push_token = graphene.String(required=True)

    Output = types.RegisterPushResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        push_token = kwargs.get('push_token')

        try:
            if user.profile.push_token == push_token:
                return types.RegisterPushResponse(ok=True)
            else: 
                user.profile.push_token = push_token
                user.profile.save()
                return types.RegisterPushResponse(ok=True)

        except IntegrityError as e:
            print(e)
            return types.RegisterPushResponse(ok=False)


class DeleteProfile(graphene.Mutation):

    Output = types.DeleteProfileResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        try:
            user.profile.delete()
            user.delete()
            return types.DeleteProfileResponse(ok=True)

        except IntegrityError as e:
            print(e)
            return types.DeleteProfileResponse(ok=False)


class UploadAvatar(graphene.Mutation):

    class Arguments:
        file = Upload(required=True)

    Output = types.UploadAvatarResponse

    @login_required
    def mutate(self, info, file, **kwargs):

        user = info.context.user

        try:
            prevMainAvatar = models.Avatar.objects.get(
                is_main=True, creator=user)
            prevMainAvatar.is_main = False
            newMainAvatar = models.Avatar.objects.create(
                is_main=True, image=file, thumbnail=file, app_thumbnail=file, creator=user)
            user.profile.avatar_url = newMainAvatar.thumbnail
            user.profile.app_avatar_url = newMainAvatar.app_thumbnail
            prevMainAvatar.save()
            user.profile.save()
            return types.UploadAvatarResponse(ok=True, preAvatarUUID=prevMainAvatar.uuid ,newAvatarUUID=newMainAvatar.uuid, avatar=newMainAvatar)

        except models.Avatar.DoesNotExist:
            newMainAvatar = models.Avatar.objects.create(
                is_main=True, image=file, thumbnail=file, app_thumbnail=file, creator=user)
            user.profile.avatar_url = newMainAvatar.thumbnail
            user.profile.app_avatar_url = newMainAvatar.app_thumbnail
            user.profile.save()
            return types.UploadAvatarResponse(ok=True, preAvatarUUID=None ,newAvatarUUID=newMainAvatar.uuid, avatar=newMainAvatar) 


class DeleteAvatar(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    Output = types.DeleteAvatarResponse

    @login_required
    def mutate(self, info,  **kwargs):

        user = info.context.user
        uuid = kwargs.get('uuid')

        try:
            avatar = models.Avatar.objects.get(uuid=uuid)
            if not avatar.is_main:
                avatar.delete()
            return types.DeleteAvatarResponse(ok=True, uuid=uuid)

        except:
            return types.DeleteAvatarResponse(ok=False, uuid=uuid)


class FacebookConnect(graphene.Mutation):

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        gender = graphene.String()
        cityId = graphene.String(required=True)
        countryCode = graphene.String(required=True)
        fbId = graphene.String(required=True)

    Output = types.FacebookConnectResponse

    def mutate(self, info, **kwargs):

        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        email = kwargs.get('email')
        gender = kwargs.get('gender')
        cityId = kwargs.get('cityId')
        countryCode = kwargs.get('countryCode')
        fbId = kwargs.get('fbId')



        try:
            profile = models.Profile.objects.get(
                fbId=fbId
            )
            token = get_token(profile.user)
            return types.FacebookConnectResponse(ok=True, token=token)

        except models.Profile.DoesNotExist:

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
                    qs = qs.filter(Q(distance__lt=max_distance))
                    for i in qs:
                        pass
                return qs

            try:
                city = location_models.City.objects.get(city_id=cityId)
            except location_models.City.DoesNotExist:
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

    
            with open('pinner/users/adjectives.json', mode='rt', encoding='utf-8') as file:
                adjectives = json.load(file)
                if email: 
                    local, at, domain = email.rpartition('@')
                username = random.choice(adjectives) + local.capitalize()

                newUser = User.objects.create_user(username)
                newUser.first_name = first_name
                newUser.last_name = last_name
                newUser.save()

                avatar_url = "https://graph.facebook.com/%s/picture?type=large" % fbId
                thumbnail = BytesIO(urlopen(avatar_url).read())
                avatar = models.Avatar.objects.create(
                    is_main=True,
                    creator=newUser,
                )
                avatar.thumbnail.save("image.jpg", ContentFile(thumbnail.getvalue()), save=False)
                avatar.save()
                profile = models.Profile.objects.create(
                    user=newUser,
                    fbId=fbId,
                    email_address=email,
                    is_verified_email_address=True,
                    gender=gender,
                    avatar_url=avatar.thumbnail,
                    app_avatar_url=avatar.thumbnail,
                    current_city=city,
                    current_country = city.country,
                    current_continent = city.country.continent,
                )

                token = get_token(profile.user)
                return types.FacebookConnectResponse(ok=True, token=token)


class SlackReportUsers(graphene.Mutation):

    class Arguments:
        targetUuid = graphene.String(required=True)
        payload = graphene.String(required=True)

    Output = types.SlackReportUsersResponse

    def mutate(self, info, **kwargs):

        reportUsername = info.context.user.username
        targetUuid = kwargs.get('targetUsername')
        targetUsername = User.objects.get(profile__uuid=targetUuid).username
        payload = kwargs.get('payload')

        if payload == "PHOTO":
            to_channel = "#user_reports"
            attachments = [{
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#80318c",
                # "pretext": "Optional text that appears above the attachment block",
                "author_name": reportUsername,
                "author_link": "https://www.pinner.fun/%s" % (reportUsername),
                "title":  "reported user: %s" % (targetUsername),
                "title_link": "https://www.pinner.fun/%s" % (targetUsername),
                "text": "%s reports that %s has inappropriate PHOTO" % (reportUsername, targetUsername),
                "footer": "🙅🏻‍♂️ Inappropriate Photo!"
            }]
            notify_slack(to_channel,  attachments)
            return types.SlackReportUsersResponse(ok=True)
        elif(payload == "SPAM"):
            to_channel = "#user_reports"
            attachments = [{
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#80318c",
                # "pretext": "Optional text that appears above the attachment block",
                "author_name": reportUsername,
                "author_link": "https://www.pinner.fun/%s" % (reportUsername),
                "title":  "reported user: %s" % (targetUsername),
                "title_link": "https://www.pinner.fun/%s" % (targetUsername),
                "text": "%s reports that %s looks like SPAM" % (reportUsername, targetUsername),
                "footer": "🤦🏻‍♂️ Spam User!"
            }]
            notify_slack(to_channel,  attachments)
            return types.SlackReportUsersResponse(ok=True)
        elif(payload == "MESSAGE"):
            to_channel = "#user_reports"
            attachments = [{
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#80318c",
                # "pretext": "Optional text that appears above the attachment block",
                "author_name": reportUsername,
                "author_link": "https://www.pinner.fun/%s" % (reportUsername),
                "title":  "reported user: %s" % (targetUsername),
                "title_link": "https://www.pinner.fun/%s" % (targetUsername),
                "text": "%s reports that %s sent inappropriate MESSAGE" % (reportUsername, targetUsername),
                "footer": "🙅🏻‍♂️ Inappropriate Message!"
            }]
            notify_slack(to_channel,  attachments)
            return types.SlackReportUsersResponse(ok=True)
        elif(payload == "OTHER"):
            to_channel = "#user_reports"
            attachments = [{
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#80318c",
                # "pretext": "Optional text that appears above the attachment block",
                "author_name": reportUsername,
                "author_link": "https://www.pinner.fun/%s" % (reportUsername),
                "title":  "reported user: %s" % (targetUsername),
                "title_link": "https://www.pinner.fun/%s" % (targetUsername),
                "text": "%s reports %s" % (reportUsername, targetUsername),
                "footer": "🤦🏻‍♂️ Other Report!"
            }]
            notify_slack(to_channel,  attachments)
            return types.SlackReportUsersResponse(ok=True)
        else:
            return types.SlackReportUsersResponse(ok=False)


class AddBlockUser(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    Output = types.BlockUserResponse

    @login_required
    def mutate(self, info, **kwargs):

        profile = info.context.user.profile

        uuid = kwargs.get('uuid')
        blockingUser = models.Profile.objects.get(uuid=uuid)

        try:
            profile.user_blocked.add(blockingUser)
            blockingUser.user_blocking.add(profile)
            profile.save()
            blockingUser.save()
            return types.BlockUserResponse(ok=True)

        except IntegrityError as e:
            print(e)
            return types.BlockUserResponse(ok=False)

class DeleteBlockUser(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    Output = types.BlockUserResponse

    @login_required
    def mutate(self, info, **kwargs):

        profile = info.context.user.profile

        uuid = kwargs.get('uuid')
        blockingUser = models.Profile.objects.get(uuid=uuid)

        try:
            profile.user_blocked.remove(blockingUser)
            blockingUser.user_blocking.remove(profile)
            return types.BlockUserResponse(ok=True)

        except IntegrityError as e:
            print(e)
            return types.BlockUseremove