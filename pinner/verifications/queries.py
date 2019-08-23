from . import types, models
from graphql_jwt.decorators import login_required


@login_required
def resolve_get_verifications(self, info, **kwargs):

    payload = kwargs.get('payload')

    try:
        verifications = models.Verification.objects.filter(payload=payload)
        return types.GetVerificationsResponse(ok=True, verifications=verifications)

    except models.Verification.DoesNotExist:
        raise Exception("Verification Not Found")
