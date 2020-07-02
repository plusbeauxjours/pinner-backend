from . import types, models
from django.utils import timezone
from django.db.models import Count, F, Q
from django.db.models.fields import DateField
from django.db.models.functions import Trunc

from graphql_jwt.decorators import login_required
from locations import models as location_models
from locations import types as location_types
from users import models as user_models


@login_required
def resolve_get_trips(self, info, **kwargs):

    uuid = kwargs.get('uuid')
    page = kwargs.get('page', 0)

    try:
        user = user_models.User.objects.prefetch_related('moveNotificationUser').get(uuid=uuid)
        trip = user.moveNotificationUser.all().order_by('-start_date', '-created_at')

        return location_types.TripResponse(trip=trip)
    except user_models.User.DoesNotExist:
        return location_types.TripResponse(trip=None)
