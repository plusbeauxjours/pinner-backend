import graphene
from . import types, mutations, queries
from users import types as user_types
from notifications import types as notification_types


class Query(object):

    header = graphene.Field(
        types.HeaderResponse,
        resolver=queries.resolve_header,
        required=True,
        args={
            'cityId': graphene.String(required=True),
            'page': graphene.Int(),
        }
    )
    city_profile = graphene.Field(
        types.CityProfileResponse,
        resolver=queries.resolve_city_profile,
        required=True,
        args={
            'cityId': graphene.String(required=True),
            "payload": graphene.String(),
            'page': graphene.Int()
        }
    )
    city_users_now = graphene.Field(
        user_types.UsersNowResponse,
        resolver=queries.resolve_city_users_now,
        required=True,
        args={
            'cityId': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    city_users_before = graphene.Field(
        notification_types.usersBeforeResponse,
        resolver=queries.resolve_city_users_before,
        required=True,
        args={
            'cityId': graphene.String(required=True),
            "payload": graphene.String(),
            'page': graphene.Int(),
            'payload': graphene.String()
        }
    )
    country_profile = graphene.Field(
        types.CountryProfileResponse,
        resolver=queries.resolve_country_profile,
        required=True,
        args={
            'countryCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    get_nationality_users = graphene.Field(
        user_types.GetUserListResponse,
        resolver=queries.resolve_get_nationality_users,
        required=True,
        args={
            'payload': graphene.String(),
            'countryCode': graphene.String(required=True),
        }
    )
    get_residence_users = graphene.Field(
        user_types.GetUserListResponse,
        resolver=queries.resolve_get_residence_users,
        required=True,
        args={
            'payload': graphene.String(),
            'countryCode': graphene.String(required=True),
        }
    )
    country_users_now = graphene.Field(
        user_types.UsersNowResponse,
        resolver=queries.resolve_country_users_now,
        required=True,
        args={
            'countryCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    country_users_before = graphene.Field(
        notification_types.usersBeforeResponse,
        resolver=queries.resolve_country_users_before,
        required=True,
        args={
            'countryCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    continent_profile = graphene.Field(
        types.ContinentProfileResponse,
        resolver=queries.resolve_continent_profile,
        required=True,
        args={
            'continentCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    continent_users_now = graphene.Field(
        user_types.UsersNowResponse,
        resolver=queries.resolve_continent_users_now,
        required=True,
        args={
            'continentCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    continent_users_before = graphene.Field(
        notification_types.usersBeforeResponse,
        resolver=queries.resolve_continent_users_before,
        required=True,
        args={
            'continentCode': graphene.String(required=True),
            'page': graphene.Int()
        }
    )
    near_cities = graphene.Field(
        types.NearCitiesResponse,
        resolver=queries.resolve_near_cities,
        required=True,
        args={
            'cityId': graphene.String(required=True),
            'page': graphene.Int(),
            "payload": graphene.String()
        }
    )
    search_countries = graphene.Field(
        types.CountriesResponse,
        resolver=queries.resolve_search_countries,
        required=True,
        args={'search': graphene.String(required=True)}
    )
    search_continents = graphene.Field(
        types.ContinentsResponse,
        resolver=queries.resolve_search_continents,
        required=True,
        args={'search': graphene.String(required=True)}
    )
    get_city_photo = graphene.Field(
        types.PhotoResponse,
        resolver=queries.resolve_get_city_photo,
        required=True,
        args={'cityId': graphene.String()}
    )

    get_countries = graphene.Field(
        types.CountriesResponse,
        resolver=queries.resolve_get_countries,
        required=True,
        args={'countryCode': graphene.String()}
    )
    get_samename_cities = graphene.Field(
        types.CitiesResponse,
        resolver=queries.resolve_get_samename_cities,
        required=True,
        args={'cityId': graphene.String()}
    )
    get_cities_page = graphene.Field(
        types.GetCitiesPageResponse,
        resolver=queries.resolve_get_cities_page,
        required=True,
        args={
            'countryCode': graphene.String(required=True),
            'page': graphene.Int()}
    )
    get_countries_page = graphene.Field(
        types.GetCountriesPageResponse,
        resolver=queries.resolve_get_countries_page,
        required=True,
        args={
            'continentCode': graphene.String(required=True),
            'page': graphene.Int()}
    )


class Mutation(object):
    create_city = mutations.CreateCity.Field(required=True)
    report_location = mutations.ReportLocation.Field(required=True)
    toggle_like_city = mutations.ToggleLikeCity.Field(required=True)
    slack_report_locations = mutations.SlackReportLocation.Field(required=True)
