import random
import math
import json

import uuid
import graphene
from django.db.models.expressions import RawSQL
from django.db import IntegrityError
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from users import models as users_models
from locations import models as location_models
from locations import types as location_types
from locations import reversePlace
from locations import locationThumbnail
from django.contrib.auth.models import User
from . import models, types
from . import sendSMS
from . import sendEMAIL


class MarkAsVerified(graphene.Mutation):

    class Arguments:
        verificationId = graphene.Int(required=True)

    Output = types.MarkAsVerifiedResponse

    @login_required
    def mutate(self, info, **kwargs):

        verificationId = kwargs.get('verificationId')
        user = info.context.user

        try:
            verification = models.Verification.objects.get(
                id=verificationId
            )
            verification.is_verified = True
            verification.save()
            return types.MarkAsVerifiedResponse(ok=True)

        except models.Verification.DoesNotExist:
            return types.MarkAsVerifiedResponse(ok=False)
            raise Exception('Verification Not Found')


class StartPhoneVerification(graphene.Mutation):

    class Arguments:
        phoneNumber = graphene.String(required=True)

    Output = types.StartPhoneVerificationResponse

    def mutate(self, info, **kwargs):

        phoneNumber = kwargs.get('phoneNumber')

        try:
            existingVerification = models.Verification.objects.get(
                payload=phoneNumber,
                target="phone",
                is_verified=False
            )
            existingVerification.delete()
            newVerification = models.Verification.objects.create(
                payload=phoneNumber,
                target="phone",
                is_verified=False
            )
            newVerification.save()
            try:
                sendSMS.sendVerificationSMS(newVerification.payload, newVerification.key)
                return types.StartPhoneVerificationResponse(ok=True)
            except:
                return types.StartPhoneVerificationResponse(ok=False)

        except IntegrityError as e:
            return types.StartPhoneVerificationResponse(ok=False)
            raise Exception("Wrong Phone Number")

        except models.Verification.DoesNotExist:
            newVerification = models.Verification.objects.create(
                payload=phoneNumber,
                target="phone",
                is_verified=False
            )
            newVerification.save()
            try:
                sendSMS.sendVerificationSMS(newVerification.payload, newVerification.key)
                return types.StartPhoneVerificationResponse(ok=True)
            except:
                return types.StartPhoneVerificationResponse(ok=False)

        except:
            return types.StartPhoneVerificationResponse(ok=False)
            raise Exception('Phone number is already verified')


class CompletePhoneVerification(graphene.Mutation):

    class Arguments:
        phoneNumber = graphene.String(required=True)
        countryPhoneNumber = graphene.String(required=True)
        countryPhoneCode = graphene.String(required=True)
        key = graphene.String(required=True)
        cityId = graphene.String(required=True)

    Output = types.CompletePhoneVerificationResponse

    def mutate(self, info, **kwargs):

        phoneNumber = kwargs.get('phoneNumber')
        countryPhoneNumber = kwargs.get('countryPhoneNumber')
        countryPhoneCode = kwargs.get('countryPhoneCode')
        key = kwargs.get('key')
        cityId = kwargs.get('cityId')

        if phoneNumber.startswith('0'):
            phoneNumber = phoneNumber.replace('0', '')
            return phoneNumber

        payload = countryPhoneNumber + phoneNumber

        try:
            verification = models.Verification.objects.get(
                key=key,
                target="phone",
                payload=payload,
                is_verified=False,
                is_edit=False
            )

            try:
                exstingUserProfile = users_models.Profile.objects.get(phone_number=phoneNumber)
                exstingUserProfile.is_verified_phone_number = True
                exstingUserProfile.save()
                verification.is_verified = True
                verification.user = exstingUserProfile.user
                verification.save()
                token = get_token(exstingUserProfile.user)
                return types.CompletePhoneVerificationResponse(ok=True, token=token)

            except users_models.Profile.DoesNotExist:

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
                        username = random.choice(adjectives) + random.choice(nouns).capitalize()
                        newUser = User.objects.create_user(username=username)
                        token = get_token(newUser)
                        city = location_models.City.objects.get(city_id=cityId)
                        newUserProfile = users_models.Profile.objects.create(
                            user=newUser,
                            country_phone_number=countryPhoneNumber,
                            country_phone_code=countryPhoneCode,
                            phone_number=phoneNumber,
                            current_city=city,
                            current_country=city.country,
                            current_continent=city.country.continent,
                        )
                        newUserProfile.is_verified_phone_number = True
                        newUserProfile.save()
                        verification.is_verified = True
                        verification.user = newUser
                        verification.save()
                        return types.CompletePhoneVerificationResponse(ok=True, token=token)

        except models.Verification.DoesNotExist:
            return types.CompletePhoneVerificationResponse(ok=False, token=None)
            raise Exception('Verification key not valid')


class StartEditPhoneVerification(graphene.Mutation):

    class Arguments:
        phoneNumber = graphene.String(required=True)
        countryPhoneNumber = graphene.String(required=True)

    Output = types.StartEditPhoneVerificationResponse

    @login_required
    def mutate(self, info, **kwargs):

        phoneNumber = kwargs.get('phoneNumber')
        countryPhoneNumber = kwargs.get('countryPhoneNumber')
        if phoneNumber.startswith('0'):
            phoneNumber = phoneNumber.replace('0', '')
            return phoneNumber
        payload = countryPhoneNumber + phoneNumber
        user = info.context.user

        try:
            existingPhoneNumber = users_models.Profile.objects.get(phone_number=phoneNumber)
            if existingPhoneNumber:
                return types.StartEditPhoneVerificationResponse(ok=False)
                raise Exception('Phone number is already verified')

        except users_models.Profile.DoesNotExist:
            try:
                preVerification = models.Verification.objects.get(payload=payload,
                                                                  target="phone",
                                                                  user=user,
                                                                  is_verified=False,
                                                                  is_edit=True)
                preVerification.delete()
                newVerification = models.Verification.objects.create(
                    payload=payload,
                    target="phone",
                    user=user,
                    is_verified=False,
                    is_edit=True
                )
                newVerification.save()
                try:
                    sendSMS.sendVerificationSMS(newVerification.payload, newVerification.key)
                    return types.StartEditPhoneVerificationResponse(ok=True)
                except:
                    newVerification.delete()
                    return types.StartEditPhoneVerificationResponse(ok=False)
            except models.Verification.DoesNotExist:
                newVerification = models.Verification.objects.create(
                    payload=payload,
                    target="phone",
                    user=user,
                    is_verified=False,
                    is_edit=True
                )
                newVerification.save()
                try:
                    sendSMS.sendVerificationSMS(newVerification.payload, newVerification.key)
                    return types.StartEditPhoneVerificationResponse(ok=True)
                except:
                    newVerification.delete()
                    return types.StartEditPhoneVerificationResponse(ok=False)


class CompleteEditPhoneVerification(graphene.Mutation):

    class Arguments:
        phoneNumber = graphene.String(required=True)
        countryPhoneNumber = graphene.String(required=True)
        countryPhoneCode = graphene.String(required=True)
        key = graphene.String(required=True)

    Output = types.CompleteEditPhoneVerificationResponse

    def mutate(self, info, **kwargs):

        phoneNumber = kwargs.get('phoneNumber')
        countryPhoneNumber = kwargs.get('countryPhoneNumber')
        countryPhoneCode = kwargs.get('countryPhoneCode')
        key = kwargs.get('key')
        payload = countryPhoneNumber + phoneNumber
        profile = info.context.user.profile

        try:
            verification = models.Verification.objects.get(
                payload=payload,
                key=key,
                target="phone",
                is_verified=False,
                is_edit=True
            )
            profile.phone_number = phoneNumber
            profile.country_phone_number = countryPhoneNumber
            profile.country_phone_code = countryPhoneCode
            profile.is_verified_phone_number = True
            profile.save()
            verification.is_verified = True
            verification.save()
            return types.CompleteEditPhoneVerificationResponse(ok=True,
                                                               phoneNumber=phoneNumber,
                                                               countryPhoneNumber=countryPhoneNumber,
                                                               countryPhoneCode=countryPhoneCode,
                                                               isVerifiedPhoneNumber=True)

        except models.Verification.DoesNotExist:
            return types.CompleteEditPhoneVerificationResponse(ok=False,
                                                               phoneNumber=None,
                                                               countryPhoneNumber=None,
                                                               countryPhoneCode=None,
                                                               isVerifiedPhoneNumber=False)
            raise Exception('Verification key not valid')


class StartEmailVerification(graphene.Mutation):

    class Arguments:
        emailAddress = graphene.String(required=True)

    Output = types.StartEmailVerificationResponse

    def mutate(self, info, **kwargs):

        emailAddress = kwargs.get('emailAddress')

        try:
            existingVerification = models.Verification.objects.get(
                payload=emailAddress,
                target="email",
                is_verified=False
            )
            existingVerification.delete()
            newVerification = models.Verification.objects.create(
                payload=emailAddress,
                target="email",
                is_verified=False
            )
            newVerification.save()
            try:
                sendEMAIL.sendVerificationEMAIL(emailAddress, newVerification.key)
                return types.StartEmailVerificationResponse(ok=True)
            except:
                return types.StartEmailVerificationResponse(ok=False)

        except models.Verification.DoesNotExist:
            newVerification = models.Verification.objects.create(
                payload=emailAddress,
                target="email",
                is_verified=False
            )
            newVerification.save()
            try:
                sendEMAIL.sendVerificationEMAIL(emailAddress, newVerification.key)
                return types.StartEmailVerificationResponse(ok=True)
            except:
                return types.StartEmailVerificationResponse(ok=False)

        except:
            raise Exception('Email address is already verified')


class CompleteEmailVerification(graphene.Mutation):

    class Arguments:
        key = graphene.String(required=True)
        cityId = graphene.String(required=True)

    Output = types.CompleteEmailVerificationResponse

    def mutate(self, info, **kwargs):

        key = kwargs.get('key')
        cityId = kwargs.get('cityId')

        try:
            verification = models.Verification.objects.get(
                key=key,
                target="email",
                is_verified=False,
                is_edit=False
            )

            try:
                exstingUserProfile = users_models.Profile.objects.get(email_address=verification.payload)
                exstingUserProfile.is_verified_email_address = True
                exstingUserProfile.save()
                verification.is_verified = True
                verification.user = exstingUserProfile.user
                verification.save()
                token = get_token(exstingUserProfile.user)
                return types.CompleteEmailVerificationResponse(ok=True, token=token)

            except users_models.Profile.DoesNotExist:

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
                        username = random.choice(adjectives) + random.choice(nouns).capitalize()
                        newUser = User.objects.create_user(username=username)
                        token = get_token(newUser)
                        city = location_models.City.objects.get(city_id=cityId)
                        newUserProfile = users_models.Profile.objects.create(
                            user=newUser,
                            email_address=verification.payload,
                            current_city=city,
                            current_country=city.country,
                            current_continent=city.country.continent,
                        )
                        newUserProfile.is_verified_email_address = True
                        newUserProfile.save()
                        verification.is_verified = True
                        verification.user = newUser
                        verification.save()
                        return types.CompleteEmailVerificationResponse(ok=True, token=token, user=verification.user)

        except models.Verification.DoesNotExist:
            return types.CompleteEditEmailVerificationResponse(ok=False,
                                                               token=None,
                                                               user=None,
                                                               )


class StartEditEmailVerification(graphene.Mutation):

    class Arguments:
        emailAddress = graphene.String(required=True)

    Output = types.StartEditEmailVerificationResponse

    @login_required
    def mutate(self, info, **kwargs):

        emailAddress = kwargs.get('emailAddress')
        user = info.context.user

        try:
            existingEmailAddress = users_models.Profile.objects.get(
                email_address=emailAddress, is_verified_email_address=True)
            if existingEmailAddress:
                return types.StartEditEmailVerificationResponse(ok=False)
                raise Exception('Email address is already verified')

        except users_models.Profile.DoesNotExist:
            try:
                preVerification = models.Verification.objects.get(
                    target="email",
                    user=user,
                    is_verified=False,
                    is_edit=True
                )
                preVerification.delete()
                newVerification = models.Verification.objects.create(
                    payload=emailAddress,
                    user=user,
                    target="email",
                    is_edit=True
                )
                newVerification.save()
                try:
                    sendEMAIL.sendConfirmEMAIL(emailAddress, newVerification.key)
                    return types.StartEditEmailVerificationResponse(ok=True)
                except:
                    newVerification.delete()
                    return types.StartEditEmailVerificationResponse(ok=False)
            except models.Verification.DoesNotExist:
                newVerification = models.Verification.objects.create(
                    payload=emailAddress,
                    target="email",
                    user=user,
                    is_verified=False,
                    is_edit=True
                )
                newVerification.save()
                try:
                    sendEMAIL.sendConfirmEMAIL(emailAddress, newVerification.key)
                    return types.StartEditEmailVerificationResponse(ok=True)
                except:
                    newVerification.delete()
                    return types.StartEditEmailVerificationResponse(ok=False)


class CompleteEditEmailVerification(graphene.Mutation):

    class Arguments:
        key = graphene.String(required=True)

    Output = types.CompleteEditEmailVerificationResponse

    def mutate(self, info, **kwargs):

        key = kwargs.get('key')

        try:
            verification = models.Verification.objects.get(
                key=key,
                target="email",
                is_verified=False,
                is_edit=True
            )
            verification.user.profile.email_address = verification.payload
            verification.user.profile.is_verified_email_address = True
            verification.user.profile.save()
            verification.is_verified = True
            token = get_token(verification.user)
            verification.save()
            return types.CompleteEditEmailVerificationResponse(ok=True,
                                                               token=token,
                                                               user=verification.user,
                                                               )

        except models.Verification.DoesNotExist:
            return types.CompleteEditEmailVerificationResponse(ok=False,
                                                               token=None,
                                                               user=None,
                                                               )
