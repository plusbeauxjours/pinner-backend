from django.db import IntegrityError
from . import types, models
from graphql_jwt.decorators import login_required
from users import models as user_models
from locations import models as location_models
from django.utils import timezone
from django.db.models import Q


@login_required
def resolve_get_matches(self, info, **kwargs):

    user = info.context.user
    page = kwargs.get('page', 0)

    blockedUser = user.blocked_user.values('id').all()
    host = user.host.exclude((Q(host__id__in=blockedUser) | Q(guest__id__in=blockedUser))).all()
    guest = user.guest.exclude((Q(host__id__in=blockedUser) | Q(guest__id__in=blockedUser))).all()

    combined = host.union(guest).order_by('-created_at')

    return types.GetMatchesResponse(matches=combined)
