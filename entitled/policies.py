"""Grouping of authorization rules around a particular resource type"""

import asyncio

from typing import Any, Callable, Generic, TypeVar

from entitled import exceptions
from entitled.rules import Rule, RuleProtocol

T = TypeVar("T")


class Policy(Generic[T]):
    """A grouping of rules refering the given resource type."""

    def __init__(
        self,
        label: str | None = None,
        rules: dict[str, list[Rule[T]]] | None = None,
    ):
        self._registry: dict[
            str,
            list[Rule[T]],
        ] = {}
        self.label = label

        if not rules:
            rules = {}

        for action, rule in rules.items():
            self.__register(action, *rule)

    def rule(self, name: str) -> Callable[[RuleProtocol[T]], RuleProtocol[T]]:
        def wrapped(func: RuleProtocol[T]):
            rule_name = name
            if self.label is not None:
                rule_name = self.label + ":" + rule_name
            new_rule = Rule[T](rule_name, func)
            self.__register(name, new_rule)
            return func

        return wrapped

    def __register(self, action: str, *rules: Rule[T]):
        if action not in self._registry:
            self._registry[action] = [*rules]

    async def grants(
        self, actor: Any, resource: T | type[T], context: dict[str, Any] | None = None
    ) -> dict[str, bool]:
        return {
            action: await self.allows(action, actor, resource, context)
            for action in self._registry
        }

    async def allows(
        self,
        action: str,
        actor: Any,
        resource: T | type[T],
        context: dict[str, Any] | None = None,
    ) -> bool:
        try:
            return await self.authorize(action, actor, resource, context)
        except exceptions.AuthorizationException:
            return False

    async def authorize(
        self,
        action: str,
        actor: Any,
        resource: T | type[T],
        context: dict[str, Any] | None = None,
    ) -> bool:
        if action not in self._registry:
            raise exceptions.UndefinedAction(
                f"Action <{action}> undefined for this policy"
            )

        if not any(
            (
                await asyncio.gather(
                    *(rule(actor, resource, context) for rule in self._registry[action])
                )
            )
        ):
            raise exceptions.AuthorizationException("Unauthorized")

        return True
