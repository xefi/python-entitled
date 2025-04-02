import re
from typing import Any, Literal

from entitled.exceptions import AuthorizationException
from entitled.policies import Policy
from entitled.response import Err, Response
from entitled.rules import Actor, Rule, RuleProto


class Client:
    def __init__(self):
        self._policy_registry: dict[type, Policy[Any]] = {}
        self._rule_registry: dict[str, Rule[Any]] = {}

    def define_rule(self, name: str, callable: RuleProto[Actor]) -> Rule[Actor]:
        rule = Rule(name, callable)
        self._rule_registry[rule.name] = rule
        return rule

    def register_policy(self, policy: Policy[Any]):
        resource_type = getattr(policy, "__orig_class__").__args__[0]
        self._policy_registry[resource_type] = policy

    def _resolve_policy(self, resource: Any) -> Policy[Any] | None:
        lookup_key = resource if isinstance(resource, type) else type(resource)
        policy = self._policy_registry.get(lookup_key, None)
        return policy

    async def inspect(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        policy = self._resolve_policy(resource)
        if policy is not None:
            return await policy.inspect(name, actor, resource, *args, **kwargs)
        return Err(f"No policy found with name '{name}'")

    async def allows(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return (await self.inspect(name, actor, resource, *args, **kwargs)).allowed()

    async def denies(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await self.allows(name, actor, resource, *args, **kwargs)

    async def authorize(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Literal[True]:
        result = await self.inspect(name, actor, resource, *args, **kwargs)
        if not result.allowed():
            raise AuthorizationException(result.message())
        return True

    async def grants(
        self,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, bool]:
        policy = self._resolve_policy(resource)
        if policy is None:
            return {}
        return await policy.grants(actor, resource, *args, **kwargs)
