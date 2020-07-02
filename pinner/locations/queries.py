from django.db import IntegrityError

from . import types, models
from graphql_jwt.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.db.models.expressions import RawSQL

from locations import models as location_models

from notifications import models as notification_models
from notifications import types as notification_types

from users import types as user_types
from users import models as user_models

from graphql_extensions.exceptions import GraphQLError


@login_required
def resolve_header(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')

    city = models.City.objects.get(city_id=cityId)

    return types.HeaderResponse(city=city)


@login_required
def resolve_search_countries(self, info, **kwargs):

    user = info.context.user

    search = kwargs.get('search')

    countries = models.Country.objects.filter(country_name__icontains=search)[:5]

    return types.CountriesResponse(countries=countries)


@login_required
def resolve_search_continents(self, info, **kwargs):

    user = info.context.user

    search = kwargs.get('search')

    continents = models.Continent.objects.filter(continent_name__icontains=search)[:5]

    return types.ContinentsResponse(continents=continents)


@login_required
def resolve_city_profile(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    payload = kwargs.get("payload")
    offset = 10 * page

    try:
        city = models.City.objects.prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')
    count = user.moveNotificationUser.values('id').filter(city__city_id=cityId).count()

    usersNow = city.currentCity.order_by('-id').distinct('id')

    if payload == "BOX":
        usersBefore = city.moveNotificationCity.exclude(
            actor__in=usersNow).order_by('-actor_id').distinct('actor_id')[:15]
    else:
        usersBefore = city.moveNotificationCity.exclude(
            actor__in=usersNow).order_by('-actor_id').distinct('actor_id')

    if page == 1:
        nextPage = page+1
        hasNextPage = offset < usersNow.count()

        return types.CityProfileResponse(page=nextPage, count=count, usersNow=usersNow, usersBefore=usersBefore, city=city, hasNextPage=hasNextPage)

    else:
        nextPage = page+1
        hasNextPage = offset < usersNow.count()
        usersNow = usersNow[offset:10 + offset]

        return types.CityProfileResponse(page=nextPage, count=count, usersNow=usersNow, usersBefore=usersBefore, city=city, hasNextPage=hasNextPage)


@login_required
def resolve_get_samename_cities(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')

    city = models.City.objects.get(city_id=cityId)
    cities = models.City.objects.filter(city_name=city.city_name)

    def get_locations_nearby_coords(latitude, longitude, max_distance=None):

        gcd_formula = "6371 * acos(cos(radians(%s)) * \
        cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)))"
        distance_raw_sql = RawSQL(
            gcd_formula,
            (latitude, longitude, latitude)
        )
        qs = cities.exclude(city_id=cityId).annotate(distance=distance_raw_sql).order_by('distance')
        return qs

    cities = get_locations_nearby_coords(city.latitude, city.longitude)

    return types.CitiesResponse(cities=cities)


@login_required
def resolve_city_users_now(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        city = models.City.objects.prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')

    usersNow = city.currentCity.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:10 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_city_users_before(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    offset = 10 * page
    payload = kwargs.get('payload')

    nextPage = page+1

    try:
        city = models.City.objects.prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')

    usersNow = city.currentCity.order_by('-id').distinct('id')
    usersBefore = city.moveNotificationCity.exclude(
        actor__in=usersNow).order_by('-actor_id').distinct('actor_id')

    if payload == "APP":
        return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=None, hasNextPage=None)
    else:
        hasNextPage = offset < usersBefore.count()

        usersBefore = usersBefore[offset:10 + offset]

        return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_country_profile(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    count = user.moveNotificationUser.values('id').filter(city__country__country_code=countryCode).count()

    cities = models.City.objects.filter(country__country_code=countryCode)

    if page == 1:
        nextPage = page+1
        hasNextPage = offset < cities.count()

        return types.CountryProfileResponse(count=count, cities=cities, page=nextPage, country=country, hasNextPage=hasNextPage)

    else:
        nextPage = page+1
        hasNextPage = offset < cities.count()
        cities = cities[offset:10 + offset]

        return types.CountryProfileResponse(count=count, cities=cities, page=nextPage, country=country, hasNextPage=hasNextPage)


@login_required
def resolve_get_cities_page(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    cities = country.cities.all()
    cityCount = cities.count()
    hasNextPage = offset < cities.count()

    cities = cities[offset:10 + offset]
    return types.GetCitiesPageResponse(cities=cities, page=nextPage, hasNextPage=hasNextPage, cityCount=cityCount)


@login_required
def resolve_get_countries_page(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    countries = continent.countries.all()
    countryCount = countries.count()
    hasNextPage = offset < countries.count()

    countries = countries[offset:10 + offset]
    return types.GetCountriesPageResponse(countries=countries, page=nextPage, hasNextPage=hasNextPage, countryCount=countryCount)


@login_required
def resolve_get_nationality_users(self, info, **kwargs):

    user = info.context.user
    payload = kwargs.get("payload")
    countryCode = kwargs.get('countryCode')

    try:
        country = models.Country.objects.get(country_code=countryCode)

        if payload == "BOX":
            users = country.nationality.order_by('-id').distinct('id')[:15]
            return user_types.GetUserListResponse(users=users)
        else:
            users = country.nationality.order_by('-id').distinct('id')
            return user_types.GetUserListResponse(users=users)

    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')


@login_required
def resolve_get_residence_users(self, info, **kwargs):

    user = info.context.user
    payload = kwargs.get("payload")
    countryCode = kwargs.get('countryCode')

    try:
        country = models.Country.objects.get(country_code=countryCode)

        if payload == "BOX":
            users = country.residence.order_by('-id').distinct('id')[:15]
            return user_types.GetUserListResponse(users=users)
        else:
            users = country.residence.order_by('-id').distinct('id')
            return user_types.GetUserListResponse(users=users)

    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')


@login_required
def resolve_country_users_now(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    usersNow = country.currentCountry.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:10 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_country_users_before(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    usersNow = country.currentCountry.order_by('-id').distinct('id')
    usersBefore = country.moveNotificationCountry.exclude(
        actor__in=usersNow).order_by('-actor_id').distinct('actor_id')

    hasNextPage = offset < usersBefore.count()

    usersBefore = usersBefore[offset:10 + offset]

    return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_get_countries(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')

    country = models.Country.objects.get(country_code=countryCode)

    countries = country.continent.countries.all().exclude(country_code=countryCode)[:15]

    return types.CountriesResponse(countries=countries)


@login_required
def resolve_continent_profile(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    count = user.moveNotificationUser.values('id').filter(
        city__country__continent__continent_code=continentCode).count()

    countries = models.Country.objects.filter(continent__continent_code=continentCode)

    continents = models.Continent.objects.all().exclude(continent_code=continentCode)

    if page == 1:
        nextPage = page+1
        hasNextPage = offset < countries.count()

        return types.ContinentProfileResponse(page=nextPage, count=count, countries=countries,  continent=continent, continents=continents, hasNextPage=hasNextPage)

    else:
        nextPage = page+1
        hasNextPage = offset < countries.count()
        countries = countries[offset:10 + offset]

        return types.ContinentProfileResponse(page=nextPage, count=count, countries=countries,  continent=continent, continents=continents, hasNextPage=hasNextPage)


@login_required
def resolve_continent_users_now(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    usersNow = continent.currentContinent.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:10 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_continent_users_before(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    usersNow = continent.currentContinent.order_by('-id').distinct('id')
    usersBefore = continent.moveNotificationContinent.exclude(
        actor__in=usersNow).order_by('-actor_id').distinct('actor_id')

    hasNextPage = offset < usersBefore.count()

    usersBefore = usersBefore[offset:10 + offset]

    return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_near_cities(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    payload = kwargs.get('payload')
    offset = 15 * page

    nextPage = page+1

    city = models.City.objects.prefetch_related('near_city').prefetch_related('near_cities').get(city_id=cityId)

    def get_locations_nearby_coords(latitude, longitude, max_distance=None):

        gcd_formula = "6371 * acos(cos(radians(%s)) * \
        cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)))"
        distance_raw_sql = RawSQL(
            gcd_formula,
            (latitude, longitude, latitude)
        )
        near_cities_from_here = city.near_city.all().exclude(city_id=cityId).annotate(distance=distance_raw_sql)
        near_cities_from_there = city.near_cities.all().exclude(city_id=cityId).annotate(distance=distance_raw_sql)

        qs = near_cities_from_here.union(near_cities_from_there).order_by('distance')
        return qs

    combined = get_locations_nearby_coords(city.latitude, city.longitude)

    hasNextPage = offset < combined.count()
    if payload == "PIN":
        cities = combined[:3]
    else:
        cities = combined[offset:15 + offset]

    return types.NearCitiesResponse(cities=cities, page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_get_city_photo(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    try:
        city = models.City.objects.get(city_id=cityId)
        photo = city.city_thumbnail
        return types.PhotoResponse(photo=photo)

    except models.City.DoesNotExist:
        return types.PhotoResponse(photo=None)
