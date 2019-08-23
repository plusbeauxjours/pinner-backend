import graphene
from graphene_django.types import DjangoObjectType
from config import types as config_types
from coffees import types as coffee_types
from users import types as user_types
from . import models


class VerificationType(DjangoObjectType):

    class Meta:
        model = models.Verification


class GetVerificationsResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    verifications = graphene.List(VerificationType)


class MarkAsVerifiedResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class StartPhoneVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class StartEditPhoneVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class CompletePhoneVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    token = graphene.String()


class CompleteEditPhoneVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    phoneNumber = graphene.String()
    countryPhoneNumber = graphene.String()
    countryPhoneCode = graphene.String()
    isVerifiedPhoneNumber = graphene.Boolean()


class StartEmailVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class StartEditEmailVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class CompleteEmailVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    user = graphene.Field(user_types.UserType)
    token = graphene.String()


class CompleteEditEmailVerificationResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    user = graphene.Field(user_types.UserType)
    token = graphene.String()
