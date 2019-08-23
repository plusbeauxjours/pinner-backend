from locations import types as location_types
from . import types, mutations, queries
import graphql_jwt
import graphene


class Query(object):

    user_profile = graphene.Field(
        types.UserProfileResponse,
        resolver=queries.resolve_profile,
        required=True,
        args={
            'username': graphene.String(required=True),
        }
    )
    me = graphene.Field(
        types.UserProfileResponse,
        resolver=queries.resolve_me,
        required=True
    )
    search_users = graphene.Field(
        types.SearchUsersResponse,
        resolver=queries.resolve_search_users,
        required=True,
        args={'search': graphene.String(required=True)}
    )
    recommend_users = graphene.Field(
        types.RecommendUsersResponse,
        resolver=queries.resolve_recommend_users,
        required=True,
        args={'page': graphene.Int()}
    )
    user_list = graphene.Field(
        types.UserListResponse,
        resolver=queries.resolve_user_list,
        required=True
    )
    top_countries = graphene.Field(
        location_types.CountriesResponse,
        resolver=queries.resolve_top_countries,
        required=True,
        args={
            'userName': graphene.String(required=True),
        }
    )
    frequent_visits = graphene.Field(
        location_types.CitiesResponse,
        resolver=queries.resolve_frequent_visits,
        required=True,
        args={
            'userName': graphene.String(required=True),
        }
    )
    top_continents = graphene.Field(
        location_types.ContinentsResponse,
        resolver=queries.resolve_top_continents,
        required=True,
        args={
            'userName': graphene.String(required=True),
        }
    )
    get_avatars = graphene.Field(
        types.AvatarListResponse,
        resolver=queries.resolve_get_avatars,
        required=True,
        args={
            'userName': graphene.String(required=True),
        }
    )
    get_avatar_detail = graphene.Field(
        types.AvatarDetailResponse,
        resolver=queries.resolve_get_avatar_detail,
        required=True,
        args={
            'avatarId': graphene.String(required=True),
        }
    )


class Mutation(object):

    edit_profile = mutations.EditProfile.Field(required=True)
    delete_profile = mutations.DeleteProfile.Field(required=True)
    change_password = mutations.ChangePassword.Field(required=True)
    log_in = graphql_jwt.ObtainJSONWebToken.Field(required=True)
    create_account = mutations.CreateAccount.Field(required=True)
    facebook_connect = mutations.FacebookConnect.Field(required=True)
    upload_avatar = mutations.UploadAvatar.Field(required=True)
    delete_avatar = mutations.DeleteAvatar.Field(required=True)
    mark_as_main = mutations.MarkAsMain.Field(required=True)
    toggle_settings = mutations.ToggleSettings.Field(required=True)
    slack_report_users = mutations.SlackReportUsers.Field(required=True)
