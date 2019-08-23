import graphene
from . import types, queries, mutations


class Query(object):

    get_verifications = graphene.Field(
        types.GetVerificationsResponse,
        resolver=queries.resolve_get_verifications,
        required=True,
        args={'payload': graphene.String()}
    )


class Mutation(object):

    mark_as_verified = mutations.MarkAsVerified.Field(required=True)
    start_phone_verification = mutations.StartPhoneVerification.Field(required=True)
    start_email_verification = mutations.StartEmailVerification.Field(required=True)
    complete_phone_verification = mutations.CompletePhoneVerification.Field(required=True)
    complete_email_verification = mutations.CompleteEmailVerification.Field(required=True)
    start_edit_phone_verification = mutations.StartEditPhoneVerification.Field(required=True)
    start_edit_email_verification = mutations.StartEditEmailVerification.Field(required=True)
    complete_edit_phone_verification = mutations.CompleteEditPhoneVerification.Field(required=True)
    complete_edit_email_verification = mutations.CompleteEditEmailVerification.Field(required=True)
