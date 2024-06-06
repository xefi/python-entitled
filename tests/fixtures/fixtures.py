import pytest

from tests.fixtures import factories


@pytest.fixture
def user_factory():
    return factories.UserFactory


@pytest.fixture
def tenant():
    return factories.TenantFactory()
