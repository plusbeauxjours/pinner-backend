import graphene

from users import schema as user_schema
from notifications import schema as notification_schema
from verifications import schema as verification_schema
from locations import schema as location_schema
from matchs import schema as match_schema


class Query(
    user_schema.Query,
    notification_schema.Query,
    verification_schema.Query,
    location_schema.Query,
    match_schema.Query,
    graphene.ObjectType
):
    pass


class Mutation(
    user_schema.Mutation,
    notification_schema.Mutation,
    verification_schema.Mutation,
    location_schema.Mutation,
    match_schema.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
