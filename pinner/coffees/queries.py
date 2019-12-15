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

    me = info.context.user

    location = kwargs.get('location')
    cityId = kwargs.get('cityId')
    countryCode = kwargs.get('countryCode')
    continentCode = kwargs.get('continentCode')
    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    if location == "city":
        try:
            city = location_models.City.objects.prefetch_related('coffee').get(city_id=cityId)
        except location_models.City.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None, count=None)

        try:
            profile = me.profile
            blockedUser = profile.blocked_user.values('id').all()
            matchedGuests = me.guest.values('host__id').all()
            matchedHosts = me.host.values('guest__id').all()
            coffees = city.coffee.filter((Q(target='everyone') |
                                          Q(target='nationality', host__profile__nationality=profile.nationality) |
                                          Q(target='residence', host__profile__residence=profile.residence) |
                                          Q(target='gender', host__profile__gender=profile.gender)) &
                                         Q(expires__gte=timezone.now())).exclude(host__id__in=matchedGuests).exclude(host__profile__id__in=blockedUser).exclude(host__id__in=matchedHosts).order_by('-created_at')
            count = coffees.count()
            return types.GetCoffeesResponse(coffees=coffees, count=count)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None, count=None)

    elif location == "profile":
        try:
            user = User.objects.prefetch_related('coffee').get(profile__uuid=uuid)
        except User.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None, count=None)

        try:
            coffees = models.Coffee.objects.filter(host=user, expires__gte=timezone.now()).order_by(
                '-created_at')
            count = coffees.count()
            return types.GetCoffeesResponse(coffees=coffees, count=count)

        except models.Coffee.DoesNotExist:
            return types.GetCoffeesResponse(coffees=None, count=None)


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
    profile = user.profile
    page = kwargs.get('page', 0)

    blockedUser = profile.blocked_user.values('id').all()
    host = user.host.exclude(( Q(host__profile__id__in=blockedUser)|  Q(guest__profile__id__in=blockedUser))).all()
    guest = user.guest.exclude(( Q(host__profile__id__in=blockedUser)|  Q(guest__profile__id__in=blockedUser))).all()

    combined = host.union(guest).order_by('-created_at')

    return types.GetMatchesResponse(matches=combined)
