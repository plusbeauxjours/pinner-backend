import graphene
from django.utils import timezone
from graphene_django.types import DjangoObjectType
from . import models

from config import types as config_types
from users import types as user_types
from notifications import types as notification_types


class CityType(DjangoObjectType):
    user_count = graphene.Int(source='user_count')
    user_log_count = graphene.Int(source='user_log_count')
    like_count = graphene.Int(source='like_count')
    distance = graphene.Int()
    count = graphene.Int()
    is_liked = graphene.Boolean()

    class Meta:
        model = models.City

    def resolve_is_liked(self, info):
        user = info.context.user
        try:
            like = models.Like.objects.get(city=self, creator=user)
            return True
        except models.Like.DoesNotExist:
            return False


class CountryType(DjangoObjectType):
    city_count = graphene.Int(source='city_count')
    total_like_count = graphene.Int(source='total_like_count')
    count = graphene.Int()

    class Meta:
        model = models.Country


class ContinentType(DjangoObjectType):
    country_count = graphene.Int(source='country_count')
    count = graphene.Int()

    class Meta:
        model = models.Continent


class HeaderResponse(graphene.ObjectType):
    city = graphene.Field(CityType)


class CreateCityResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    cityId = graphene.String()
    countryCode = graphene.String()
    continentCode = graphene.String()


class PhotoResponse(graphene.ObjectType):
    photo = graphene.String()


class CityProfileResponse(graphene.ObjectType):
    page = graphene.Int()
    count = graphene.Int()
    city = graphene.Field(CityType)
    usersNow = graphene.List(user_types.UserType)
    usersBefore = graphene.List(notification_types.MoveNotificationType)
    hasNextPage = graphene.Boolean()


class GetCitiesPageResponse(graphene.ObjectType):
    page = graphene.Int()
    hasNextPage = graphene.Boolean()
    cityCount = graphene.Int()
    cities = graphene.List(CityType)


class GetCountriesPageResponse(graphene.ObjectType):
    page = graphene.Int()
    hasNextPage = graphene.Boolean()
    countryCount = graphene.Int()
    countries = graphene.List(CountryType)


class CountryProfileResponse(graphene.ObjectType):
    page = graphene.Int()
    count = graphene.Int()
    country = graphene.Field(CountryType)
    cities = graphene.List(CityType)
    hasNextPage = graphene.Boolean()


class ContinentProfileResponse(graphene.ObjectType):
    page = graphene.Int()
    count = graphene.Int()
    countries = graphene.List(CountryType)
    continent = graphene.Field(ContinentType)
    continents = graphene.List(ContinentType)
    hasNextPage = graphene.Boolean()


class CitiesResponse(graphene.ObjectType):
    cities = graphene.List(CityType)


class NearCitiesResponse(graphene.ObjectType):
    page = graphene.Int()
    hasNextPage = graphene.Boolean()
    cities = graphene.List(CityType)


class CountriesResponse(graphene.ObjectType):
    countries = graphene.List(CountryType)


class ContinentsResponse(graphene.ObjectType):
    continents = graphene.List(ContinentType)


class TripResponse(graphene.ObjectType):
    trip = graphene.List(notification_types.MoveNotificationType)


class ReportLocationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class ToggleLikeCityResponse(graphene.ObjectType):
    city = graphene.Field(CityType)
    ok = graphene.Boolean()


class SlackReportLocationResponse(graphene.ObjectType):
    ok = graphene.Boolean()


class GetSameTripsResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    count = graphene.Int()
    cities = graphene.List(CityType)
