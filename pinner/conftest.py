import pytest
from django.conf import settings
from django.test import RequestFactory

from pinner.users.tests.factories import UserFactory


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()
