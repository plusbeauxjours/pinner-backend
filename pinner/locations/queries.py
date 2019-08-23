from django.db import IntegrityError

from . import types, models
from graphql_jwt.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.db.models.expressions import RawSQL

from django.contrib.auth.models import User

from notifications import models as notification_models
from notifications import types as notification_types

from coffees import models as coffee_models

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

    countries = models.Country.objects.filter(country_name__istartswith=search)[:5]

    return types.CountriesResponse(countries=countries)


@login_required
def resolve_search_continents(self, info, **kwargs):

    user = info.context.user

    search = kwargs.get('search')

    continents = models.Continent.objects.filter(continent_name__istartswith=search)[:5]

    return types.ContinentsResponse(continents=continents)


@login_required
def resolve_trip_profile(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    startDate = kwargs.get('startDate')
    endDate = kwargs.get('endDate')

    try:
        city = models.City.objects.prefetch_related(
            'moveNotificationCity').prefetch_related('coffee').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('Trip not found')

    count = user.moveNotificationUser.values('id').filter(city__city_id=cityId).count()

    usersBefore = city.moveNotificationCity.filter(Q(start_date__lte=(endDate)) |
                                                   Q(end_date__gte=(startDate))).order_by('actor_id').distinct('actor_id')

    userCount = usersBefore.count()

    coffees = city.coffee.filter(created_at__range=(startDate, endDate))[:42]

    return types.TripProfileResponse(count=count, city=city, usersBefore=usersBefore, userCount=userCount, coffees=coffees)


@login_required
def resolve_city_profile(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')

    try:
        city = models.City.objects.prefetch_related('coffee').prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')

    count = user.moveNotificationUser.values('id').filter(city__city_id=cityId).count()

    coffees = city.coffee.filter(expires__gt=timezone.now())
    usersNow = city.currentCity.order_by('-id').distinct('id')
    hasNextPage = 20 < usersNow.count()
    usersBefore = city.moveNotificationCity.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')[:20]
    usersNow = usersNow[:20]

    return types.CityProfileResponse(count=count, usersNow=usersNow, usersBefore=usersBefore, city=city, hasNextPage=hasNextPage)


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
    offset = 20 * page

    nextPage = page+1

    try:
        city = models.City.objects.prefetch_related('coffee').prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')

    usersNow = city.currentCity.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:20 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_city_users_before(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        city = models.City.objects.prefetch_related('coffee').prefetch_related('currentCity').get(city_id=cityId)
    except models.City.DoesNotExist:
        raise GraphQLError('City not found')

    usersNow = city.currentCity.order_by('-id').distinct('id')
    usersBefore = city.moveNotificationCity.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')

    hasNextPage = offset < usersBefore.count()

    usersBefore = usersBefore[offset:20 + offset]

    return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_country_profile(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    count = user.moveNotificationUser.values('id').filter(city__country__country_code=countryCode).count()

    usersNow = country.currentCountry.order_by('-id').distinct('id')

    usersBefore = country.moveNotificationCountry.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')[:20]

    cities = models.City.objects.filter(country__country_code=countryCode)
    hasNextPage = 20 < cities.count()
    cities = cities[:20]

    return types.CountryProfileResponse(count=count, cities=cities, usersNow=usersNow, usersBefore=usersBefore, country=country, hasNextPage=hasNextPage)


@login_required
def resolve_get_cities_page(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    cities = country.cities.all()
    cityCount = cities.count()
    hasNextPage = offset < cities.count()

    cities = cities[offset:20 + offset]
    return types.GetCitiesPageResponse(cities=cities, page=nextPage, hasNextPage=hasNextPage, cityCount=cityCount)


@login_required
def resolve_get_countries_page(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    countries = continent.countries.all()
    countryCount = countries.count()
    hasNextPage = offset < countries.count()

    countries = countries[offset:20 + offset]
    return types.GetCountriesPageResponse(countries=countries, page=nextPage, hasNextPage=hasNextPage, countryCount=countryCount)


@login_required
def resolve_country_users_now(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    usersNow = country.currentCountry.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:20 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_country_users_before(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        country = models.Country.objects.get(country_code=countryCode)
    except models.Country.DoesNotExist:
        raise GraphQLError('Country not found')

    usersNow = country.currentCountry.order_by('-id').distinct('id')
    usersBefore = country.moveNotificationCountry.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')

    hasNextPage = offset < usersBefore.count()

    usersBefore = usersBefore[offset:20 + offset]

    return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_get_countries(self, info, **kwargs):

    user = info.context.user
    countryCode = kwargs.get('countryCode')

    country = models.Country.objects.get(country_code=countryCode)

    countries = country.continent.countries.all()[:20]

    return types.CountriesResponse(countries=countries)


@login_required
def resolve_continent_profile(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    count = user.moveNotificationUser.values('id').filter(
        city__country__continent__continent_code=continentCode).count()

    usersNow = continent.currentContinent.order_by('-id').distinct('id')
    usersBefore = continent.moveNotificationContinent.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')[:20]

    countries = models.Country.objects.filter(continent__continent_code=continentCode)
    hasNextPage = 20 < countries.count()
    countries = countries[:20]

    continents = models.Continent.objects.all()

    return types.ContinentProfileResponse(count=count, countries=countries,  usersNow=usersNow, usersBefore=usersBefore, continent=continent, continents=continents, hasNextPage=hasNextPage)


@login_required
def resolve_continent_users_now(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    usersNow = continent.currentContinent.order_by('-id').distinct('id')

    hasNextPage = offset < usersNow.count()

    usersNow = usersNow[offset:20 + offset]

    return user_types.UsersNowResponse(usersNow=usersNow,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_continent_users_before(self, info, **kwargs):

    user = info.context.user
    continentCode = kwargs.get('continentCode')
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    try:
        continent = models.Continent.objects.get(continent_code=continentCode)
    except models.Continent.DoesNotExist:
        raise GraphQLError('Continent not found')

    usersNow = continent.currentContinent.order_by('-id').distinct('id')
    usersBefore = continent.moveNotificationContinent.exclude(
        actor__profile__in=usersNow).order_by('-actor_id').distinct('actor_id')

    hasNextPage = offset < usersBefore.count()

    usersBefore = usersBefore[offset:20 + offset]

    return notification_types.usersBeforeResponse(usersBefore=usersBefore,  page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_near_cities(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    page = kwargs.get('page', 0)
    offset = 20 * page

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

    combined = combined[offset:20 + offset]

    return types.NearCitiesResponse(cities=combined, page=nextPage, hasNextPage=hasNextPage)


@login_required
def resolve_get_city_photo(self, info, **kwargs):

    user = info.context.user
    cityId = kwargs.get('cityId')
    try:
        city = models.City.objects.get(city_id=cityId)
        photo = city.city_photo
        return types.PhotoResponse(photo=photo)

    except models.City.DoesNotExist:
        return types.PhotoResponse(photo=None)


@login_required
def resolve_recommend_locations(self, info, **kwargs):

    user = info.context.user
    page = kwargs.get('page', 0)
    offset = 20 * page

    nextPage = page+1

    city = user.profile.current_city

    combined = models.City.objects.order_by('-created_at')[:3]

    def get_locations_nearby_coords(latitude, longitude, max_distance=None):

        gcd_formula = "6371 * acos(cos(radians(%s)) * \
        cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)))"
        distance_raw_sql = RawSQL(
            gcd_formula,
            (latitude, longitude, latitude)
        )

        qs = combined.exclude(id=city.id).annotate(distance=distance_raw_sql).order_by('distance')
        return qs

    try:
        nationalityUser = user.profile.nationality.nationality.all().order_by('-distance')[:10]
        for i in nationalityUser:
            nationalityUsers = models.City.objects.filter(id=i.user.profile.current_city.id)
            combined = combined | nationalityUsers
    except:
        nationalityUser = user_models.Profile.objects.none()
        combined = combined | nationalityUser

    try:
        residenceUser = user.profile.residence.residence.all().order_by('-distance')[:10]
        for i in residenceUser:
            residenceUsers = models.City.objects.filter(id=i.user.profile.current_city.id)
            combined = combined | residenceUsers
    except:
        residenceUser = user_models.Profile.objects.none()
        combined = combined | residenceUser

    try:
        locationUser = user_models.Profile.objects.filter(
            user__moveNotificationUser__city=city).order_by('-distance')[:20]
        for i in locationUser:
            locationUsers = models.City.objects.filter(id=i.user.profile.current_city.id)
            combined = combined | locationUsers
    except:
        locationUser = user_models.Profile.objects.none()
        combined = combined | locationUser

    try:
        likeUser = user_models.Profile.objects.filter(user__likes__city=city).order_by('-distance')[:20]
        for i in likeUser:
            likeUsers = models.City.objects.filter(id=i.user.profile.current_city.id)
            combined = combined | likeUsers
    except:
        likeUser = user_models.Profile.objects.none()
        combined = combined | likeUser

    cities = get_locations_nearby_coords(city.latitude, city.longitude)

    hasNextPage = offset < cities.count()
    cities = cities[offset:20 + offset]

    return types.RecommendLocationsResponse(cities=cities, page=nextPage, hasNextPage=hasNextPage)
