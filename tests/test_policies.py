import pytest

from entitled.client import Client
from entitled.policies import Policy, rule
from entitled.response import Err, Ok, Response
from tests.data.models import Tenant, User

pytestmark = pytest.mark.anyio

client = Client()


class TenantPolicy(Policy[Tenant]):
    @rule
    async def is_member(
        self,
        actor: User,
        resource: Tenant,
    ) -> bool:
        return actor.tenant == resource

    @rule
    async def is_owner(
        self,
        actor: User,
        resource: Tenant,
    ) -> Response:
        return Ok() if resource.owner == actor else Err("Not owner on the tenant")


async def test_register():
    client._register_policy(TenantPolicy)
    assert Tenant in client._policy_registry


async def test_inspect():
    tenant1 = Tenant("tenant1")
    tenant2 = Tenant("tenant2")
    user1 = User("user1", tenant1, set())
    user2 = User("user2", None, set())
    tenant2.owner = user2

    assert await client.inspect("is_member", user1, tenant1)
