import pytest

from _pytest import fixtures

from tests.data import factories

pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=[pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop")],
)
def anyio_backend(request: fixtures.SubRequest):
    return request.param


@pytest.fixture
def user():
    return factories.UserFactory


@pytest.fixture
def tenant():
    return factories.TenantFactory()
