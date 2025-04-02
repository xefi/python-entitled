"""Grouping of authorization rules around a particular resource type"""

from typing import Any, TypeVar

from entitled import exceptions
from entitled.response import Err, Response
from entitled.rules import Rule, RuleProto

T = TypeVar("T")


class Policy[T]:
    """A grouping of rules refering the given resource type."""

    _registry: dict[str, Rule[Any]]

    def __init__(
        self,
        rules: dict[str, Rule[Any]] | None = None,
    ):
        self._registry = {}

        if not rules:
            rules = {}

        for action, rule in rules.items():
            self.register(action, *rule)

    def rule(self, func: RuleProto[Any]):
        rule_name = f"{func.__name__}"
        new_rule = Rule[T](rule_name, func)
        self.register(rule_name, new_rule)
        return func

    def register(self, action: str, rule: Rule[T]):
        self._registry[action] = rule

    async def inspect(
        self,
        action: str,
        actor: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        if action not in self._registry:
            return Err(f"Action <{action}> undefined for this policy")
        return await self._registry[action].inspect(actor, *args, **kwargs)

    async def allows(
        self,
        action: str,
        actor: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return (await self.inspect(action, actor, *args, **kwargs)).allowed()

    async def denies(
        self,
        action: str,
        actor: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not (await self.inspect(action, actor, *args, **kwargs)).allowed()

    async def authorize(
        self,
        action: str,
        actor: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        res = await self.inspect(action, actor, *args, **kwargs)
        if not res.allowed():
            raise exceptions.AuthorizationException(res.message())
        return True

    async def grants(
        self,
        actor: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, bool]:
        return {
            action: await self.allows(
                action,
                actor,
                *args,
                **kwargs,
            )
            for action in self._registry
        }
