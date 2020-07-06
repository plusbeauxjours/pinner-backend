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


class UpdateSNS(graphene.Mutation):

    class Arguments:
        payload = graphene.String(required=True)
        username = graphene.String(required=True)

    Output = types.UpdateSNSResponse

    @login_required
    def mutate(self, info,  **kwargs):

        user = info.context.user
        payload = kwargs.get('payload')
        username = kwargs.get('username')

        if payload == "INSTAGRAM":
            try:
                user.send_instagram = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "PHONE":
            try:
                user.send_phone = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "EMAIL":
            try:
                user.send_email = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "KAKAOTALK":
            try:
                user.send_kakao = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "FACEBOOK":
            try:
                user.send_facebook = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "YOUTUBE":
            try:
                user.send_youtube = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "TWITTER":
            try:
                user.send_twitter = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "TELEGRAM":
            try:
                user.send_telegram = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "SNAPCHAT":
            try:
                user.send_snapchat = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "LINE":
            try:
                user.send_line = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "WECHAT":
            try:
                user.send_wechat = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "KIK":
            try:
                user.send_kik = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "VK":
            try:
                user.send_vk = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "WHATSAPP":
            try:
                user.send_whatsapp = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "BEHANCE":
            try:
                user.send_behance = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "LINKEDIN":
            try:
                user.send_linkedin = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "PINTEREST":
            try:
                user.send_pinterest = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "VINE":
            try:
                user.send_vine = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)
        if payload == "TUMBLR":
            try:
                user.send_tumblr = username
                user.save()
                return types.UpdateSNSResponse(ok=True, user=user)
            except:
                return types.UpdateSNSResponse(ok=False, user=None)


class ToggleSettings(graphene.Mutation):

    class Arguments:
        payload = graphene.String(required=True)

    Output = types.ToggleSettingsResponse

    @login_required
    def mutate(self, info,  **kwargs):

        user = info.context.user
        payload = kwargs.get('payload')
        if payload == "DARK_MODE":
            if user.is_dark_mode == True:
                try:
                    user.is_dark_mode = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_dark_mode == False:
                try:
                    user.is_dark_mode = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_PHOTOS":
            if user.is_hide_photos == True:
                try:
                    user.is_hide_photos = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_hide_photos == False:
                try:
                    user.is_hide_photos = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_TRIPS":
            if user.is_hide_trips == True:
                try:
                    user.is_hide_trips = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_hide_trips == False:
                try:
                    user.is_hide_trips = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_CITIES":
            if user.is_hide_cities == True:
                try:
                    user.is_hide_cities = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_hide_cities == False:
                try:
                    user.is_hide_cities = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_COUNTRIES":
            if user.is_hide_countries == True:
                try:
                    user.is_hide_countries = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_hide_countries == False:
                try:
                    user.is_hide_countries = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "HIDE_CONTINENTS":
            if user.is_hide_continents == True:
                try:
                    user.is_hide_continents = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_hide_continents == False:
                try:
                    user.is_hide_continents = True
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
        elif payload == "AUTO_LOCATION_REPORT":
            if user.is_auto_location_report == True:
                try:
                    user.is_auto_location_report = False
                    user.save()
                    return types.ToggleSettingsResponse(ok=True, user=user)
                except:
                    return types.ToggleSettingsResponse(ok=False, user=None)
            elif user.is_auto_location_report == False:
                try:
                    user.is_auto_location_report = True
                    user.save()
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

        if user.is_authenticated:

            bio = kwargs.get('bio', user.bio)
            gender = kwargs.get('gender', user.gender)
            firstName = kwargs.get('firstName', user.first_name)
            lastName = kwargs.get('lastName', user.last_name)
            username = kwargs.get('username', user.username)
            nationalityCode = kwargs.get('nationalityCode', user.nationality)
            residenceCode = kwargs.get('residenceCode', user.residence)

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
                user.bio = bio
                user.gender = gender
                user.nationality = nationality
                user.residence = residence
                user.save()

                user.first_name = firstName
                user.last_name = lastName
                if user.username != username:
                    try:
                        existing_user = models.User.objects.get(username=username)
                        raise Exception("Username is already taken")
                    except models.User.DoesNotExist:
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
                user.avatar_url = newMainAvatar.thumbnail
                user.app_avatar_url = newMainAvatar.app_thumbnail
                user.save()
                prevMainAvatar.save()
                newMainAvatar.save()
                return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar,  preAvatarUUID=prevMainAvatar.uuid, newAvatarUUID=uuid)
            else:
                newMainAvatar = models.Avatar.objects.get(uuid=uuid)
                newMainAvatar.is_main = True
                user.avatar_url = newMainAvatar.thumbnail
                user.app_avatar_url = newMainAvatar.app_thumbnail
                user.save()
                newMainAvatar.save()
                return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar,  preAvatarUUID=None, newAvatarUUID=uuid)

        except models.Avatar.DoesNotExist:
            newMainAvatar = models.Avatar.objects.get(uuid=uuid)
            newMainAvatar.is_main = True
            user.avatar_url = newMainAvatar.thumbnail
            user.app_avatar_url = newMainAvatar.app_thumbnail
            user.save()
            newMainAvatar.save()
            return types.MarkAsMainResponse(ok=True, avatar=newMainAvatar, preAvatarUUID=None, newAvatarUUID=uuid)


class RegisterPush(graphene.Mutation):

    class Arguments:
        push_token = graphene.String(required=True)

    Output = types.RegisterPushResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        push_token = kwargs.get('push_token')

        try:
            if user.push_token == push_token:
                return types.RegisterPushResponse(ok=True)
            else:
                user.push_token = push_token
                user.save()
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
            user.delete()
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
            prevMainAvatar = models.Avatar.objects.filter(
                is_main=True, creator=user)
            prevMainAvatar.update(is_main=False)
            newMainAvatar = models.Avatar.objects.create(
                is_main=True, image=file, thumbnail=file, app_thumbnail=file, creator=user)
            user.avatar_url = newMainAvatar.thumbnail
            user.app_avatar_url = newMainAvatar.app_thumbnail
            prevMainAvatar.save()
            user.save()
            return types.UploadAvatarResponse(ok=True, preAvatarUUID=prevMainAvatar.uuid, newAvatarUUID=newMainAvatar.uuid, avatar=newMainAvatar)

        except models.Avatar.DoesNotExist:
            newMainAvatar = models.Avatar.objects.create(
                is_main=True, image=file, thumbnail=file, app_thumbnail=file, creator=user)
            user.avatar_url = newMainAvatar.thumbnail
            user.app_avatar_url = newMainAvatar.app_thumbnail
            user.save()
            return types.UploadAvatarResponse(ok=True, preAvatarUUID=None, newAvatarUUID=newMainAvatar.uuid, avatar=newMainAvatar)


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
            user = models.User.objects.get(
                fbId=fbId
            )
            token = get_token(user)
            return types.FacebookConnectResponse(ok=True, token=token)

        except models.User.DoesNotExist:

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

                newUser = models.User.objects.create_user(username)
                newUser.first_name = first_name
                newUser.last_name = last_name

                avatar_url = "https://graph.facebook.com/%s/picture?type=large" % fbId
                # thumbnail = BytesIO(urlopen(avatar_url).read())
                # avatar = models.Avatar.objects.create(
                #     is_main=True,
                #     creator=newUser,
                # )
                # avatar.thumbnail.save("image.jpg", ContentFile(thumbnail.getvalue()), save=False)
                # avatar.save()

                newUser.fbId = fbId
                newUser.email_address = email
                newUser.is_verified_email_address = True
                newUser.gender = gender
                newUser.avatar_url = avatar_url
                newUser.app_avatar_url = avatar_url
                newUser.current_city = city
                newUser.current_country = city.country
                newUser.current_continent = city.country.continent
                newUser.save()
                moveNotification = notification_models.MoveNotification.objects.create(
                    actor=newUser,
                    city=city,
                    country=city.country,
                    continent=city.country.continent,
                )

                token = get_token(newUser)
                return types.FacebookConnectResponse(ok=True, token=token)


class AppleConnect(graphene.Mutation):

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        cityId = graphene.String(required=True)
        countryCode = graphene.String(required=True)
        appleId = graphene.String(required=True)

    Output = types.AppleConnectResponse

    def mutate(self, info, **kwargs):

        first_name = kwargs.get('first_name')
        last_name = kwargs.get('last_name')
        email = kwargs.get('email')
        gender = kwargs.get('gender')
        cityId = kwargs.get('cityId')
        countryCode = kwargs.get('countryCode')
        appleId = kwargs.get('appleId')

        try:
            user = models.User.objects.get(
                appleId=appleId
            )
            token = get_token(user)
            return types.AppleConnectResponse(ok=True, token=token)

        except models.User.DoesNotExist:

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

            with open('pinner/users/adjectives.json', mode='rt', encoding='utf-8') as adjectives:
                with open('pinner/users/nouns.json', mode='rt', encoding='utf-8') as nouns:
                    adjectives = json.load(adjectives)
                    nouns = json.load(nouns)

                    if email:
                        local, at, domain = email.rpartition('@')
                        username = random.choice(adjectives) + local.capitalize()
                        is_verified_email_address = True
                    else:
                        username = random.choice(adjectives) + random.choice(nouns).capitalize()
                        is_verified_email_address = False

                    newUser = models.User.objects.create_user(username)
                    if first_name:
                        newUser.first_name = first_name
                    if last_name:
                        newUser.last_name = last_name
                    newUser.save()
                    newUser.appleId = appleId
                    newUser.email_address = email
                    newUser.is_verified_email_address = is_verified_email_address
                    newUser.gender = gender
                    newUser.current_city = city
                    newUser.current_country = city.country
                    newUser.current_continent = city.country.continent
                    newUser.save()

                    moveNotification = notification_models.MoveNotification.objects.create(
                        actor=newUser,
                        city=city,
                        country=city.country,
                        continent=city.country.continent,
                    )

                    token = get_token(newUser)
                    return types.AppleConnectResponse(ok=True, token=token)


class SlackReportUsers(graphene.Mutation):

    class Arguments:
        targetUuid = graphene.String(required=True)
        payload = graphene.String(required=True)

    Output = types.SlackReportUsersResponse

    def mutate(self, info, **kwargs):

        reportUsername = info.context.user.username
        targetUuid = kwargs.get('targetUsername')
        targetUsername = models.User.objects.get(uuid=targetUuid).username
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

    Output = types.AddBlockUserResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        uuid = kwargs.get('uuid')
        blockedUser = models.User.objects.get(uuid=uuid)

        try:
            user.blocked_user.add(blockedUser)
            user.save()
            return types.AddBlockUserResponse(ok=True, blockedUser=blockedUser)

        except IntegrityError as e:
            print(e)
            return types.AddBlockUserResponse(ok=False, blockedUser=None)


class DeleteBlockUser(graphene.Mutation):

    class Arguments:
        uuid = graphene.String(required=True)

    Output = types.DeleteBlockUserResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        uuid = kwargs.get('uuid')
        blockedUser = models.User.objects.get(uuid=uuid)

        try:
            user.blocked_user.remove(blockedUser)
            return types.DeleteBlockUserResponse(ok=True, uuid=uuid)

        except IntegrityError as e:
            print(e)
            return types.DeleteBlockUserResponse(ok=False, uuid=None)
