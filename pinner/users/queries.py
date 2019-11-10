import graphene
from graphql_jwt.decorators import login_required
from django.contrib.auth.models import User
from . import types, models
from django.db.models import Count, F, Sum, Q
from locations import types as location_types
from locations import models as location_models
from notifications import models as notification_models


def resolve_profile(self, info, **kwargs):

    username = kwargs.get('username')

    try:
        profile = User.objects.get(username=username)
        return types.UserProfileResponse(user=profile)

    except User.DoesNotExist:
        return types.UserProfileResponse(user=None)


def resolve_get_same_trips(self, info, **kwargs):

    username = kwargs.get('username')

    Auser = info.context.user
    Buser = User.objects.get(username=username)

    try:
        ATrips = Auser.moveNotificationUser.values('city')
        BTrips = Buser.moveNotificationUser.values('city')
        Trips = ATrips.intersection(BTrips)
        cities = location_models.City.objects.filter(id__in=Trips)
        count = cities.count()
        return location_types.GetSameTripsResponse(ok=True, cities=cities, count=count)

    except User.DoesNotExist:
        return location_types.GetSameTripsResponse(ok=False, cities=None, count=None)


def resolve_get_avatars(self, info, **kwargs):

    user = info.context.user
    userName = kwargs.get('userName')

    try:
        avatars = models.Avatar.objects.filter(creator__username=userName)
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
    userName = kwargs.get('userName')
    page = kwargs.get('page', 0)
    offset = 6 * page

    nextPage = page+1

    countries = location_models.Country.objects.filter(
        cities__moveNotificationCity__actor__username=userName).annotate(
        count=Count('cities__moveNotificationCity', distinct=True)).annotate(
        diff=Sum('cities__moveNotificationCity__diff_days')).order_by('-count', '-diff')

    hasNextPage = offset < countries.count()
    usersNow = countries[offset:6 + offset]

    return location_types.CountriesResponse(page=nextPage, hasNextPage=hasNextPage, countries=countries)


@login_required
def resolve_frequent_visits(self, info, **kwargs):

    user = info.context.user
    userName = kwargs.get('userName')
    page = kwargs.get('page', 0)
    offset = 6 * page

    nextPage = page+1

    cities = location_models.City.objects.filter(
        moveNotificationCity__actor__username=userName).annotate(
        count=Count('moveNotificationCity', distinct=True)).annotate(
        diff=Sum('moveNotificationCity__diff_days')).order_by('-count', '-diff')

    hasNextPage = offset < cities.count()
    usersNow = cities[offset:6 + offset]

    return location_types.CitiesResponse(page=nextPage, hasNextPage=hasNextPage, cities=cities)


@login_required
def resolve_top_continents(self, info, **kwargs):

    user = info.context.user
    userName = kwargs.get('userName')
    page = kwargs.get('page', 0)
    offset = 6 * page

    nextPage = page+1

    continents = location_models.Continent.objects.filter(
        countries__cities__moveNotificationCity__actor__username=userName).annotate(
        count=Count('countries__cities__moveNotificationCity', distinct=True)).annotate(
        diff=Sum('countries__cities__moveNotificationCity__diff_days')).order_by('-count', '-diff')

    hasNextPage = offset < continents.count()
    usersNow = continents[offset:6 + offset]

    return location_types.ContinentsResponse(page=nextPage, hasNextPage=hasNextPage, continents=continents)


@login_required
def resolve_me(self, info):

    user = info.context.user

    return types.UserProfileResponse(user=user)


@login_required
def resolve_search_users(self, info, **kwargs):

    user = info.context.user

    search = kwargs.get('search')

    users = User.objects.filter(username__istartswith=search)[:5]

    return types.SearchUsersResponse(users=users)


@login_required
def resolve_recommend_users(self, info, **kwargs):

    user = info.context.user
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1
    userGuest = user.guest.all()
    userHost = user.host.all()

    combined = models.Profile.objects.none()

    try:
        nationalityUser = user.profile.nationality.nationality.all().order_by('-distance')[:10]
        combined = combined | nationalityUser.exclude(id=user.profile.id).exclude(Q(user__host__in=userGuest) | Q(
            user__host__in=userHost) | Q(user__guest__in=userGuest) | Q(user__guest__in=userHost)).order_by('id').distinct('id')
    except:
        nationalityUser = models.Profile.objects.none()

    try:
        residenceUser = user.profile.residence.residence.all().order_by('-distance')[:10]
        combined = combined | residenceUser.exclude(id=user.profile.id).exclude(Q(user__host__in=userGuest) | Q(
            user__host__in=userHost) | Q(user__guest__in=userGuest) | Q(user__guest__in=userHost)).order_by('id').distinct('id')
    except:
        residenceUser = models.Profile.objects.none()

    try:
        locationUser = user.moveNotificationUser.all().order_by('-created_at').order_by('city').distinct('city')[:10]
        for i in locationUser:
            userLocations = models.Profile.objects.filter(user__moveNotificationUser__city=i.city).order_by('-distance')
            combined = combined | userLocations.exclude(id=user.profile.id).exclude(Q(user__host__in=userGuest) | Q(
                user__host__in=userHost) | Q(user__guest__in=userGuest) | Q(user__guest__in=userHost)).order_by('id').distinct('id')
    except:
        locationUser = models.Profile.objects.none()

    hasNextPage = offset < combined.count()
    combined = combined[offset:20 + offset]

    return types.RecommendUsersResponse(users=combined, page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_user_list(self, info):

    user = info.context.user

    users = models.User.objects.all().exclude(pk=user.pk).order_by(
        '-date_joined')

    return types.UserListResponse(users=users)
