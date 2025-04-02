import pytest

from _pytest import fixtures

pytestmark = pytest.mark.anyio


@pytest.fixture(
    params=[pytest.param(("asyncio", {"use_uvloop": True}), id="asyncio+uvloop")],
)
def anyio_backend(request: fixtures.SubRequest):
    return request.param
