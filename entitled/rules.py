"""Basic building block of the Entitled library.

Rules are essentially wrappers around boolean functions that determines a relationship
between an actor and a resourc.

Resource can essentially be any entity in an application.
Actors represents any entity that, in an application, can act upon a resource.
"""

from typing import Any, Callable, Generic, Protocol, TypeVar

from entitled import exceptions

Resource = TypeVar("Resource", contravariant=True)


class RuleProtocol(Protocol[Resource]):
    """Defines valid functions for rules"""

    def __call__(
        self, actor: Any, resource: Resource, context: dict[str, Any] | None = None
    ) -> bool: ...


class Rule(Generic[Resource]):
    """Base class for rules

    Args:
        name (str): The name given to this rule.
        rule_function (Callable): The underlying boolean function.
    """

    _registry: dict[str, "Rule"] = {}

    @classmethod
    def clear_registry(cls) -> None:
        cls._registry = {}

    @classmethod
    def get_rule(cls, name) -> "Rule | None":
        return Rule._registry[name] if name in Rule._registry else None

    def __init__(self, name: str, rule_function: RuleProtocol[Resource]):
        if name in Rule._registry:
            raise ValueError(f"A rule identified by '{name}' already exists.")
        self.name = name
        self.rule = rule_function
        Rule._registry[name] = self

    def __call__(
        self,
        actor: Any,
        resource: Resource,
        context: dict | None = None,
    ) -> bool:
        if not context:
            context = {}
        return self.rule(actor, resource, context)

    def __and__(self, rh_rule: "Rule[Resource]"):
        return Rule(
            f"{self.name}&{rh_rule.name}",
            lambda actor, resource, context=None: (
                self(actor, resource, context) and rh_rule(actor, resource, context)
            ),
        )

    def __or__(self, rh_rule: "Rule[Resource]"):
        return Rule(
            f"{self.name}|{rh_rule.name}",
            lambda actor, resource, context=None: (
                self(actor, resource, context) or rh_rule(actor, resource, context)
            ),
        )

    def authorize(
        self,
        actor: Any,
        resource: Resource,
        context: dict | None = None,
    ) -> bool:
        if not self(actor, resource, context):
            raise exceptions.AuthorizationException("Unauthorized")
        return True

    def allows(
        self,
        actor: Any,
        resource: Resource,
        context: dict | None = None,
    ) -> bool:
        return self(actor, resource, context)


def rule(name: str) -> Callable[[RuleProtocol], RuleProtocol]:
    def wrapped(func: RuleProtocol):
        Rule(name, func)
        return func

    return wrapped
