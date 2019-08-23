import graphene
from graphene_django.types import DjangoObjectType
from . import models
from django.contrib.auth.models import User
from config import types as config_types


class CoffeeType(DjangoObjectType):
    natural_time = graphene.String(source='natural_time')
    status = graphene.String(source='status')

    class Meta:
        model = models.Coffee


class MatchType(DjangoObjectType):
    natural_time = graphene.String(source='natural_time')
    is_host = graphene.Boolean()
    is_guest = graphene.Boolean()
    is_matching = graphene.Boolean()

    def resolve_is_host(self, info):
        user = info.context.user
        if self in user.host.all():
            return True
        else:
            return False

    def resolve_is_guest(self, info):
        user = info.context.user
        if self in user.guest.all():
            return True
        else:
            return False

    def resolve_is_matching(self, info):
        user = info.context.user
        if self in user.host.all() or user.guest.all():
            return True
        else:
            return False

    class Meta:
        model = models.Match


class RequestCoffeeResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    coffee = graphene.Field(CoffeeType)


class GetCoffeesResponse(graphene.ObjectType):
    coffees = graphene.List(CoffeeType)


class GetMatchesResponse(graphene.ObjectType):
    matches = graphene.List(MatchType)


class CoffeeDetailResponse(graphene.ObjectType):
    coffee = graphene.Field(CoffeeType)


class MatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    coffeeId = graphene.String()
    cityId = graphene.String()
    countryCode = graphene.String()
    continentCode = graphene.String()
    match = graphene.Field(MatchType)


class UnMatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    matchId = graphene.String()
    cityId = graphene.String()
    countryCode = graphene.String()
    continentCode = graphene.String()
    coffee = graphene.Field(CoffeeType)


class DeleteCoffeeResponse(graphene.ObjectType):
    username = graphene.String()
    coffeeId = graphene.String()
    ok = graphene.Boolean()


class MarkAsReadMatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    matchId = graphene.String()
    isReadByHost = graphene.Boolean()
    isReadByGuest = graphene.Boolean()
