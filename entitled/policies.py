"""Grouping of authorization rules around a particular resource type"""

from typing import Generic, TypeVar

from entitled import exceptions
from entitled.rules import Rule

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
            self.register(action, *rule)

    def rule(self, action, rule):
        rule_name = action if self.label is None else self.label + ":" + action
        new_rule = Rule[T](rule_name, rule)

        self.register(action, new_rule)

    def register(self, action, *rules: Rule[T]):
        if action in self._registry:
            self._registry[action].append(*rules)
        else:
            self._registry[action] = [*rules]

    def actions(self, actor, resource: T, context: dict | None = None):

        return filter(
            lambda action: self.allows(actor, action, resource, context),
            self._registry.keys(),
        )

    def allows(
        self,
        actor,
        action,
        resource: T,
        context: dict | None = None,
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
        context: dict | None = None,
    ) -> bool:
        if action not in self._registry:
            raise exceptions.UndefinedAction(
                f"Action <{action}> undefined for this policy"
            )

        if not any(rule(actor, resource, context) for rule in self._registry[action]):
            raise exceptions.AuthorizationException("Unauthorized")

        return True
