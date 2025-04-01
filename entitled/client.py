from typing import Any, Literal

from entitled.exceptions import AuthorizationException
from entitled.response import Err, Response
from entitled.rules import Actor, Rule, RuleProto


class Client:
    def __init__(self):
        self._rule_registry: dict[str, Rule[Any]] = {}

    def define_rule(self, name: str, callable: RuleProto[Actor]) -> Rule[Actor]:
        rule = Rule(name, callable)
        self._rule_registry[rule.name] = rule
        return rule

    async def inspect(
        self,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        if name in self._rule_registry:
            return await self._rule_registry[name].inspect(actor, *args, **kwargs)
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
