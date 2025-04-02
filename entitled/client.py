from typing import Any, Literal

from entitled.exceptions import AuthorizationException
from entitled.policies import Policy
from entitled.response import Err, Response
from entitled.rules import Actor, Rule, RuleProto


class Client:
    def __init__(self):
        self._policy_registry: dict[type, type[Policy[Any]]] = {}
        self._rule_registry: dict[str, Rule[Any]] = {}

    def define_rule(self, name: str, callable: RuleProto[Actor]) -> Rule[Actor]:
        rule = Rule(name, callable)
        self._rule_registry[rule.name] = rule
        return rule

    def _register_policy(self, policy: type[Policy[Any]]):
        resource_type = getattr(policy, "__orig_bases__")[0].__args__[0]
        self._policy_registry[resource_type] = policy

    def _resolve_rule(self, name: str, resource: Any) -> Rule[Any] | None:
        lookup_key = resource if isinstance(resource, type) else type(resource)
        policy = self._policy_registry.get(lookup_key, None)
        if policy is not None:
            rule = getattr(policy, name, None)
            if rule is not None and hasattr(rule, "_is_rule"):
                return Rule(name, rule)
        return self._rule_registry.get(name, None)

    async def inspect(
        self,
        name: str,
        actor: Actor,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        rule = self._resolve_rule(name, resource)
        if rule is not None:
            return await rule.inspect(actor, resource, *args, **kwargs)
        return Err(f"No rule found with name '{name}'")

    async def allows(
        self,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        if name in self._rule_registry:
            return await self._rule_registry[name].allows(actor, *args, **kwargs)
        return False

    async def denies(
        self,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not self.allows(name, actor, *args, **kwargs)

    async def authorize(
        self,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> Literal[True]:
        if name in self._rule_registry:
            return await self._rule_registry[name].authorize(actor, *args, **kwargs)
        raise AuthorizationException(f"No rule found with name '{name}'")
