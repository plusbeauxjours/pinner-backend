import graphene
from users import models as user_models
from config import types as config_types
from graphene_django.types import DjangoObjectType
from . import models


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


class TokenType(DjangoObjectType):
    username = graphene.String(source='username')
    photo_count = graphene.Int(source='photo_count')
    city_count = graphene.Int(source='city_count')
    country_count = graphene.Int(source='country_count')
    continent_count = graphene.Int(source='continent_count')
    post_count = graphene.Int(source='post_count')
    trip_count = graphene.Int(source='trip_count')
    blocked_user_count = graphene.Int(source='blocked_user_count')
    is_self = graphene.Boolean()

    def resolve_is_self(self, info):
        user = info.context.user
        if self.id == user.id:
            return True
        else:
            return False

    class Meta:
        model = user_models.User


class GetMatchesResponse(graphene.ObjectType):
    matches = graphene.List(MatchType)


class MatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    match = graphene.Field(MatchType)


class UnMatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    matchId = graphene.Int()


class MarkAsReadMatchResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    matchId = graphene.String()
    isReadByHost = graphene.Boolean()
    isReadByGuest = graphene.Boolean()
