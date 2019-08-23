import graphene
from graphene_django.types import DjangoObjectType


class ResponseFields(graphene.AbstractType):
    ok = graphene.Boolean(required=True)
    error = graphene.String()
