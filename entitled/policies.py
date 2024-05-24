"""Grouping of authorization rules around a particular resource type"""

import typing

from entitled import exceptions
from entitled.rules import Rule

T = typing.TypeVar("T")


class Policy(typing.Generic[T]):
    """A grouping of rules refering the given resource type."""

    def __init__(
        self,
        rules: typing.Optional[dict[str, list[Rule[typing.Any, T]]]] = None,
    ):
        self._registry: dict[
            str,
            list[Rule[typing.Any, T]],
        ] = {}

        if not rules:
            rules = {}

        for action, rule in rules.items():
            self.register(action, *rule)

    def register(self, action, *rules: Rule[typing.Any, T]):
        if action in self._registry:
            self._registry[action].append(*rules)
        else:
            self._registry[action] = [*rules]

    def actions(self, actor, resource: T, context: typing.Optional[dict] = None):

        return filter(
            lambda action: self.allows(actor, action, resource, context),
            self._registry.keys(),
        )

    def allows(
        self,
        actor,
        action,
        resource: T,
        context: typing.Optional[dict] = None,
    ) -> bool:
        try:
            return self.authorize(actor, action, resource, context)
        except exceptions.AuthorizationException:
            return False

    def authorize(
        self,
        actor,
        action,
        resource: T,
        context: typing.Optional[dict] = None,
    ) -> bool:
        if action not in self._registry:
            raise exceptions.UndefinedAction(
                f"Action <{action}> undefined for this policy"
            )

        if not any(rule(actor, resource, context) for rule in self._registry[action]):
            raise exceptions.AuthorizationException("Unauthorized")

        return True
