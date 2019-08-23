import graphene
from graphene_django.types import DjangoObjectType
from config import types as config_types
from . import models
from graphene.types.union import Union


class NotificationType(DjangoObjectType):
    natural_time = graphene.String(source="natural_time")
    created_at = graphene.Date(source="created_at")

    class Meta:
        model = models.Notification


class MoveNotificationType(DjangoObjectType):
    natural_time = graphene.String(source="natural_time")
    created_at = graphene.Date(source="created_at")
    diff_days = graphene.Int(source="diff_days")

    class Meta:
        model = models.MoveNotification


class MarkAsReadResponse(graphene.ObjectType):
    notificationId = graphene.Int()
    ok = graphene.Boolean()


class AddTripResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    moveNotification = graphene.Field(MoveNotificationType)
    distance = graphene.Int()


class EditTripResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    moveNotification = graphene.Field(MoveNotificationType)
    distance = graphene.Int()


class DeleteTripResponse(graphene.ObjectType):
    ok = graphene.Boolean()
    distance = graphene.Int()
    tripId = graphene.Int()


class CalculateDistanceResponse(graphene.ObjectType):
    distance = graphene.Int()


class DurationTripsResponse(graphene.ObjectType):
    moveNotifications = graphene.List(MoveNotificationType)


class usersBeforeResponse(graphene.ObjectType):
    page = graphene.Int()
    hasNextPage = graphene.Boolean()
    usersBefore = graphene.List(MoveNotificationType)
