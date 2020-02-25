from . import types, models
from django.utils import timezone
from django.db.models import Count, F, Q
from django.db.models.fields import DateField
from django.db.models.functions import Trunc

from graphql_jwt.decorators import login_required
from locations import models as location_models
from django.contrib.auth.models import User
from locations import types as location_types
from coffees import models as coffees_models


@login_required
def resolve_get_trips(self, info, **kwargs):

    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    try:
        user = User.objects.prefetch_related('moveNotificationUser').get(profile__uuid=uuid)
        trip = user.moveNotificationUser.all().order_by('-start_date', '-created_at')

        return location_types.TripResponse(trip=trip)
    except models.User.DoesNotExist:
        return location_types.TripResponse(trip=None)

# 2020/02/25

# @login_required
# def resolve_get_trip_cities(self, info, **kwargs):

#     user = info.context.user

#     try:
#         trip = user.moveNotificationUser.all().order_by('city',).distinct('city')
#         try:
#             coffees = coffees_models.Coffee.objects.get(host=user, expires__gte=timezone.now())
#             coffeeId = coffees.uuid
#             return location_types.TripCitiesResponse(trip=trip, coffeeId=coffeeId)
#         except coffees_models.Coffee.DoesNotExist:
#             return location_types.TripCitiesResponse(trip=trip, coffeeId=None)
#     except models.User.DoesNotExist:
#         return location_types.TripCitiesResponse(trip=None, coffeeId=None)
