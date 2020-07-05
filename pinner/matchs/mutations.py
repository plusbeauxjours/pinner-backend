import graphene
from django.db import IntegrityError
from . import models, types
from graphql_jwt.decorators import login_required
from locations import models as location_models
from notifications import models as notification_models
from users import models as user_models
from django.db.models import Q


class Match(graphene.Mutation):

    class Arguments:
        cityId = graphene.String(required=True)
        hostUuid = graphene.String(required=True)
        guestUuid = graphene.String(required=True)

    Output = types.MatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user

        cityId = kwargs.get('cityId')
        hostUuid = kwargs.get('hostUuid')
        guestUuid = kwargs.get('guestUuid')

        try:
            host = user_models.User.objects.get(uuid=hostUuid)
            guest = user_models.User.objects.get(uuid=guestUuid)
            city = location_models.City.objects.get(city_id=cityId)
            try:
                existingMatch = models.Match.objects.get(Q(host=host, guest=guest) | Q(host=guest, guest=host))
                return types.MatchResponse(ok=True, match=existingMatch)
            except models.Match.DoesNotExist:
                match = models.Match.objects.create(
                    city=city,
                    host=host,
                    guest=guest,
                )
                notification_models.Notification.objects.create(
                    verb="match",
                    actor=user,
                    target=guest,
                    match=match
                )
                return types.MatchResponse(ok=True, match=match)
        except IntegrityError as e:
            print(e)
            raise Exception("Can't create a match")


class UnMatch(graphene.Mutation):

    class Arguments:
        matchId = graphene.Int(required=True)

    Output = types.UnMatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        user = info.context.user
        matchId = kwargs.get('matchId')

        try:
            match = models.Match.objects.get(id=matchId)
            match.delete()
            return types.UnMatchResponse(ok=True, matchId=matchId,)
        except models.Match.DoesNotExist:
            return types.UnMatchResponse(ok=False, matchId=None, )


class MarkAsReadMatch(graphene.Mutation):

    class Arguments:
        matchId = graphene.Int(required=True)

    Output = types.MarkAsReadMatchResponse

    @login_required
    def mutate(self, info, **kwargs):

        matchId = kwargs.get('matchId')
        user = info.context.user

        try:
            match = models.Match.objects.get(
                id=matchId
            )
            if user == match.host:
                match.is_read_by_host = True
                match.save()
                return types.MarkAsReadMatchResponse(ok=True, matchId=matchId, isReadByHost=match.is_read_by_host, isReadByGuest=match.is_read_by_guest)
            elif user == match.guest:
                match.is_read_by_guest = True
                match.save()
                return types.MarkAsReadMatchResponse(ok=True, matchId=matchId, isReadByHost=match.is_read_by_host, isReadByGuest=match.is_read_by_guest)
            else:
                return types.MarkAsReadMatchResponse(ok=False, matchId=None, isReadByHost=None, isReadByGuest=None)

        except models.Match.DoesNotExist:
            raise Exception('This match is already unmatched ')
