import pytest
from entitled.client import Client
from entitled.exceptions import AuthorizationException
from entitled.policies import Policy
from entitled.response import Err, Ok, Response
from tests.data.factories import TenantFactory, UserFactory
from tests.data.models import Tenant, User

pytestmark = pytest.mark.anyio

client = Client()
policy = Policy[Tenant]()


@policy.rule
async def is_member(
    actor: User,
    resource: Tenant,
) -> bool:
    return actor.tenant == resource


@policy.rule
async def is_owner(
    actor: User,
    resource: Tenant,
    context: str,
) -> Response:
    return (
        Ok()
        if len(context) > 0 and resource.owner == actor
        else Err("Not owner on the tenant")
    )


tenant1 = TenantFactory()
tenant2 = TenantFactory()
user1 = UserFactory(tenant=tenant1)
user2 = UserFactory(tenant=tenant2)
tenant2.owner = user2
client.register_policy(policy)


async def test_inspect():
    res = await client.inspect(
        "is_member",
        user1,
        tenant1,
    )
    assert res.allowed()
    res = await client.inspect(
        "is_member",
        user2,
        tenant1,
    )
    assert res.message() == "Unauthorized"


async def test_allows():
    assert await client.allows(
        "is_member",
        user1,
        tenant1,
    )
    assert await client.denies(
        "is_member",
        user2,
        tenant1,
    )


async def test_authorize():
    assert await client.authorize(
        "is_member",
        user1,
        tenant1,
    )
    with pytest.raises(AuthorizationException):
        _ = await client.authorize(
            "is_member",
            user2,
            tenant1,
        )


async def test_grants():
    res = await client.grants(user1, tenant1, context="ok")
    assert res["is_member"]
    assert not res["is_owner"]
