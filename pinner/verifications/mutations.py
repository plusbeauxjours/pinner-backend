import random
import math
import json

import uuid
import graphene
from django.db import IntegrityError
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import get_token
from graphql_extensions.exceptions import GraphQLError
from users import models as users_models
from locations import models as location_models
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
