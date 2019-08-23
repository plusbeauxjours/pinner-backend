from django.db import IntegrityError
from . import types, models
from django.contrib.auth.models import User
from graphql_jwt.decorators import login_required
from locations import models as location_models
from coffees import models as coffee_models
from django.utils import timezone
from django.db.models import Q


@login_required
def resolve_get_coffees(self, info, **kwargs):

    user = info.context.user
    me = info.context.user

    location = kwargs.get('location')
    cityId = kwargs.get('cityId')
    countryCode = kwargs.get('countryCode')
    continentCode = kwargs.get('continentCode')
    userName = kwargs.get('userName')
    if location == "city":
        try:
            city = location_models.City.objects.prefetch_related('coffee').get(city_id=cityId)
        except location_models.City.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

        try:
            profile = me.profile
            matchedGuests = me.guest.values('host__id').all()
            matchedHosts = me.host.values('guest__id').all()
            coffees = city.coffee.filter((Q(target='everyone') |
                                          Q(target='nationality', host__profile__nationality=profile.nationality) |
                                          Q(target='residence', host__profile__residence=profile.residence) |
                                          Q(target='gender', host__profile__gender=profile.gender)) &
                                         Q(expires__gte=timezone.now())).exclude(host__id__in=matchedGuests).exclude(host__id__in=matchedHosts).order_by('-created_at')
            return types.GetCoffeesResponse(coffees=coffees)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

    elif location == "profile":
        try:
            user = User.objects.prefetch_related('coffee').get(username=userName)
        except User.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

        try:
            coffees = models.Coffee.objects.filter(host=user, expires__gte=timezone.now()).order_by(
                '-created_at')
            return types.GetCoffeesResponse(coffees=coffees)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

    elif location == "history":
        try:
            user = User.objects.prefetch_related('coffee').get(username=userName)
        except User.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

        try:
            coffees = user.coffee.all()
            return types.GetCoffeesResponse(coffees=coffees)
        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

    elif location == "country":
        try:
            allCities = location_models.City.objects.values('id').filter(country__country_code=countryCode)
        except location_models.City.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

        try:
            profile = me.profile
            matchedMatch = me.guest.values('id').all()

            coffees = coffee_models.Coffee.objects.filter((Q(target='everyone') |
                                                           Q(target='nationality', host__profile__nationality=profile.nationality) |
                                                           Q(target='residence', host__profile__residence=profile.residence) |
                                                           Q(target='gender', host__profile__gender=profile.gender)) &
                                                          Q(expires__gte=timezone.now()) & Q(city__id__in=allCities)).exclude(match__id__in=matchedMatch).order_by('-created_at')

            return types.GetCoffeesResponse(coffees=coffees)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

    elif location == "continent":

        try:
            allCities = location_models.City.objects.values('id').filter(
                country__continent__continent_code=continentCode)
        except location_models.City.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)

        try:
            profile = me.profile
            matchedMatch = me.guest.values('id').all()
            coffees = coffee_models.Coffee.objects.filter((Q(target='everyone') |
                                                           Q(target='nationality', host__profile__nationality=profile.nationality) |
                                                           Q(target='residence', host__profile__residence=profile.residence) |
                                                           Q(target='gender', host__profile__gender=profile.gender)) &
                                                          Q(expires__gte=timezone.now()) & Q(city__id__in=allCities)).exclude(match__id__in=matchedMatch).order_by('-created_at')

            return types.GetCoffeesResponse(coffees=coffees)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None)


@login_required
def resolve_coffee_detail(self, info, **kwargs):

    coffeeId = kwargs.get('coffeeId')
    user = info.context.user

    if coffeeId:
        try:
            coffee = models.Coffee.objects.get(uuid=coffeeId)
        except models.Coffee.DoesNotExist:
            raise Exception('coffee not found')

    return types.CoffeeDetailResponse(coffee=coffee)


@login_required
def resolve_get_matches(self, info, **kwargs):

    user = info.context.user
    matchPage = kwargs.get('matchPage', 0)

    host = user.host.all()
    guest = user.guest.all()

    if (matchPage is 0):
        combined = host.union(guest).order_by('-created_at')[:20]
    else:
        combined = host.union(guest).order_by('-created_at')[20:]

    return types.GetMatchesResponse(matches=combined)
