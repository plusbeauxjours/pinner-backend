from . import types, models
from django.db.models import Count, F, Q
from django.db.models.fields import DateField
from django.db.models.functions import Trunc

from graphql_jwt.decorators import login_required
from locations import models as location_models
from django.contrib.auth.models import User
from locations import types as location_types


@login_required
def resolve_get_trips(self, info, **kwargs):

    username = kwargs.get('username')
    page = kwargs.get('page', 0)
    offset = 10 * page

    nextPage = page+1

    try:
        user = User.objects.prefetch_related('moveNotificationUser').get(username=username)
        trip = user.moveNotificationUser.all().order_by('-start_date', '-created_at')

        hasNextPage = offset < trip.count()
        trip = trip[offset:10 + offset]

        return location_types.TripResponse(page=nextPage, hasNextPage=hasNextPage, trip=trip)
    except models.City.DoesNotExist:
        return location_types.TripResponse(page=None, hasNextPage=None, trip=None)
