import graphene
from . import types, queries, mutations
from locations import types as location_types


class Query(object):

    get_trips = graphene.Field(
        location_types.TripResponse,
        resolver=queries.resolve_get_trips,
        required=True,
        args={
            'uuid': graphene.String(required=True),
            'page': graphene.Int(),
        }
    )
    get_trip_cities = graphene.Field(
        location_types.TripResponse,
        resolver=queries.resolve_get_trip_cities,
        required=True,
        args={
            'page': graphene.Int(),
        }
    )


class Mutation(object):

    mark_as_read = mutations.MarkAsRead.Field(required=True)
    add_trip = mutations.AddTrip.Field(required=True)
    edit_trip = mutations.EditTrip.Field(required=True)
    delete_trip = mutations.DeleteTrip.Field(required=True)
    calculate_distance = mutations.CalculateDistance.Field(required=True)
