import graphene
from django.db import IntegrityError
from . import models, types
from math import radians, degrees, sin, cos, asin, acos, sqrt
from graphql_jwt.decorators import login_required

from locations import models as location_models


class MarkAsRead(graphene.Mutation):

    class Arguments:
        notificationId = graphene.Int(required=True)

    Output = types.MarkAsReadResponse

    @login_required
    def mutate(self, info, **kwargs):

        notificationId = kwargs.get('notificationId')
        user = info.context.user

        try:
            notification = models.Notification.objects.get(
                id=notificationId
            )
            notification.is_read = True
            notification.save()
            return types.MarkAsReadResponse(ok=True, notificationId=notificationId)

        except models.Notification.DoesNotExist:
            raise Exception('Notification Not Found')


class AddTrip(graphene.Mutation):

    class Arguments:
        cityId = graphene.String(required=True)
        startDate = graphene.types.datetime.DateTime(required=True)
        endDate = graphene.types.datetime.DateTime(required=True)

    Output = types.AddTripResponse

    @login_required
    def mutate(self, info, **kwargs):

        cityId = kwargs.get('cityId')
        startDate = kwargs.get('startDate')
        endDate = kwargs.get('endDate')
        user = info.context.user

        try:
            moveNotification = models.MoveNotification.objects.create(
                actor=user,
                city=location_models.City.objects.get(city_id=cityId),
                country=location_models.Country.objects.get(cities__city_id=cityId),
                continent=location_models.Continent.objects.get(countries__cities__city_id=cityId),
                start_date=startDate,
                end_date=endDate
            )
            return types.AddTripResponse(ok=True, moveNotification=moveNotification)
        except IntegrityError as e:
            print(e)
            raise Exception("Can't create the trip")


class EditTrip(graphene.Mutation):

    class Arguments:
        moveNotificationId = graphene.Int(required=True)
        cityId = graphene.String()
        startDate = graphene.types.datetime.DateTime()
        endDate = graphene.types.datetime.DateTime()

    Output = types.EditTripResponse

    @login_required
    def mutate(self, info, **kwargs):

        moveNotificationId = kwargs.get('moveNotificationId')
        user = info.context.user

        try:
            moveNotification = user.moveNotificationUser.get(id=moveNotificationId)
        except user.moveNotificationUser.DoesNotExist:
            raise Exception('Trip Not Found')

        if moveNotification.actor.id != user.id:
            raise Exception('Unauthorized')

        else:
            try:
                cityId = kwargs.get('cityId', moveNotification.city.city_id)
                startDate = kwargs.get('startDate', moveNotification.start_date)
                endDate = kwargs.get('endDate', moveNotification.end_date)

                moveNotification.city = location_models.City.objects.get(city_id=cityId)
                moveNotification.country = location_models.Country.objects.get(cities__city_id=cityId)
                moveNotification.continent = location_models.Continent.objects.get(countries__cities__city_id=cityId)
                moveNotification.start_date = startDate
                moveNotification.end_date = endDate

                moveNotification.save()
                return types.EditTripResponse(ok=True, moveNotification=moveNotification)
            except IntegrityError as e:
                print(e)
                raise Exception("Can't Save Trip")


class DeleteTrip(graphene.Mutation):

    class Arguments:
        moveNotificationId = graphene.Int(required=True)

    Output = types.DeleteTripResponse

    @login_required
    def mutate(self, info, **kwargs):

        moveNotificationId = kwargs.get('moveNotificationId')
        user = info.context.user

        try:
            moveNotification = user.moveNotificationUser.get(id=moveNotificationId)
        except user.moveNotificationUser.DoesNotExist:
            raise Exception('Trip Not Found')

        if moveNotification.actor.id == user.id:

            moveNotification.delete()
            return types.DeleteTripResponse(ok=True, tripId=moveNotificationId)

        else:
            raise Exception('You need to log in')


class CalculateDistance(graphene.Mutation):

    Output = types.CalculateDistanceResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        distance = 0

        try:
            trips = models.MoveNotification.objects.filter(actor=user).order_by('-start_date', '-created_at')
        except user.moveNotificationUser.DoesNotExist:
            raise Exception('Trips Not Found')

        try:
            for i, trip in enumerate(trips):
                try:
                    lon1, lat1, lon2, lat2 = map(
                        radians, [trips[i].city.longitude, trips[i].city.latitude, trips[i+1].city.longitude, trips[i+1].city.latitude])
                    dist = 6371 * (
                        acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
                    )
                    distance += dist
                except (ZeroDivisionError, IndexError) as e:
                    print(e)

            user.profile.distance = int(round(distance))
            user.profile.save()
            return types.CalculateDistanceResponse(distance=int(round(distance)))

        except IntegrityError as e:
            raise Exception("Can't Like City")
