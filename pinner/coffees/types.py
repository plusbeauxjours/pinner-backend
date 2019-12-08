import graphene
from graphene_django.types import DjangoObjectType
from . import models
from django.contrib.auth.models import User
from config import types as config_types


class CoffeeType(DjangoObjectType):
    natural_time = graphene.String(source='natural_time')
    status = graphene.String(source='status')
    match_count = graphene.Int(source='match_count')
    is_matching = graphene.Boolean()

    def resolve_is_matching(self, info):
        user = info.context.user
        if user.host.filter(coffee=self) or user.guest.filter(coffee=self):
            return True
        else:
            return False

    class Meta:
        model = models.Coffee


class MatchType(DjangoObjectType):
    natural_time = graphene.String(source='natural_time')
    is_host = graphene.Boolean()
    is_guest = graphene.Boolean()
    is_matching = graphene.Boolean()
    last_message_at = graphene.String()

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
    count = graphene.Int()
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
    matchId = graphene.Int()
    cityId = graphene.String()
    countryCode = graphene.String()
    continentCode = graphene.String()


class DeleteCoffeeResponse(graphene.ObjectType):
    uuid = graphene.String()
    coffeeId = graphene.String()
    ok = graphene.Boolean()


class MarkAsReadMatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    matchId = graphene.String()
    isReadByHost = graphene.Boolean()
    isReadByGuest = graphene.Boolean()
