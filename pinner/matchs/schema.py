import graphene
from . import types, queries, mutations


class Query(object):

    get_matches = graphene.Field(
        types.GetMatchesResponse,
        resolver=queries.resolve_get_matches,
        required=True,
        args={
            'page': graphene.Int(),
        }
    )


class Mutation(object):

    match = mutations.Match.Field(required=True)
    un_match = mutations.UnMatch.Field(required=True)
    mark_as_read_match = mutations.MarkAsReadMatch.Field(required=True)
