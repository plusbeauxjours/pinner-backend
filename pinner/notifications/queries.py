from . import types, models
from django.utils import timezone
from django.db.models import Count, F, Q
from django.db.models.fields import DateField
from django.db.models.functions import Trunc

from graphql_jwt.decorators import login_required
from locations import models as location_models
from django.contrib.auth.models import User
from locations import types as location_types
from coffees import models as coffees_types


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


@login_required
def resolve_get_trip_cities(self, info, **kwargs):

    user = info.context.user

    try:
        trip = user.moveNotificationUser.all().order_by('city',).distinct('city')
        coffees = coffees_types.Coffee.objects.filter(host=user, expires__gte=timezone.now()).order_by(
            '-created_at')
        hasCoffees = coffees.exists()
        return location_types.TripCitiesResponse(trip=trip, hasCoffees=hasCoffees)
    except models.User.DoesNotExist:
        return location_types.TripCitiesResponse(trip=None, hasCoffees=None)
