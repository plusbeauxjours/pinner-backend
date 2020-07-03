import graphene
from graphql_jwt.decorators import login_required
from . import types, models
from django.db.models import Count, F, Sum, Q
from locations import types as location_types
from locations import models as location_models
from notifications import models as notification_models


def resolve_profile(self, info, **kwargs):

    uuid = kwargs.get('uuid')

    try:
        user = models.User.objects.get(uuid=uuid)
        return types.UserProfileResponse(user=user)

    except models.User.DoesNotExist:
        return types.UserProfileResponse(user=None)


def resolve_get_same_trips(self, info, **kwargs):

    uuid = kwargs.get('uuid')

    Auser = info.context.user
    Buser = models.User.objects.get(uuid=uuid)

    try:
        ATrips = Auser.moveNotificationUser.values('city')
        BTrips = Buser.moveNotificationUser.values('city')
        Trips = ATrips.intersection(BTrips)
        cities = location_models.City.objects.filter(id__in=Trips)
        count = cities.count()
        return location_types.GetSameTripsResponse(ok=True, cities=cities, count=count)

    except models.User.DoesNotExist:
        return location_types.GetSameTripsResponse(ok=False, cities=None, count=None)


def resolve_get_avatars(self, info, **kwargs):

    user = info.context.user
    uuid = kwargs.get('uuid')

    try:
        avatars = models.Avatar.objects.filter(creator__uuid=uuid)
        return types.AvatarListResponse(avatars=avatars)
    except models.Avatar.DoesNotExist:
        return types.AvatarListResponse(avatars=None)


def resolve_get_avatar_detail(self, info, **kwargs):

    user = info.context.user
    avatarId = kwargs.get('avatarId')

    try:
        avatar = models.Avatar.objects.get(uuid=avatarId)
        return types.AvatarDetailResponse(avatar=avatar)
    except models.Avatar.DoesNotExist:
        return types.AvatarDetailResponse(avatar=None)


@login_required
def resolve_top_countries(self, info, **kwargs):

    user = info.context.user
    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    countries = location_models.Country.objects.filter(
        cities__moveNotificationCity__actor__uuid=uuid).annotate(
        count=Count('cities__moveNotificationCity', distinct=True)).order_by('-count')

    return location_types.CountriesResponse(countries=countries)


@login_required
def resolve_frequent_visits(self, info, **kwargs):

    user = info.context.user
    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    cities = location_models.City.objects.filter(
        moveNotificationCity__actor__uuid=uuid).annotate(
        count=Count('moveNotificationCity', distinct=True)).order_by('-count')

    return location_types.CitiesResponse(cities=cities)


@login_required
def resolve_top_continents(self, info, **kwargs):

    user = info.context.user
    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    continents = location_models.Continent.objects.filter(
        countries__cities__moveNotificationCity__actor__uuid=uuid).annotate(
        count=Count('countries__cities__moveNotificationCity', distinct=True)).order_by('-count')

    return location_types.ContinentsResponse(continents=continents)


@login_required
def resolve_me(self, info):

    user = info.context.user
    users = models.User.objects.all()

    return types.UserProfileResponse(user=user)


@login_required
def resolve_search_users(self, info, **kwargs):

    user = info.context.user

    search = kwargs.get('search')

    users = models.User.objects.filter(username__istartswith=search)[:5]

    return types.SearchUsersResponse(users=users)


@login_required
def resolve_user_list(self, info):

    user = info.context.user

    users = models.User.objects.all().exclude(pk=user.pk).order_by(
        '-date_joined')

    return types.UserListResponse(users=users)


@login_required
def resolve_get_blocked_user(self, info, **kwargs):

    user = info.context.user

    try:
        blocked_users = user.blocked_user.all()
        return types.GetBlockedUserResponse(blocked_users=blocked_users)
    except models.User.DoesNotExist:
        return types.GetBlockedUserResponse(blocked_users=None)
