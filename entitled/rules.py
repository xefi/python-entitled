"""Basic building block of the Entitled library.

Rules are essentially wrappers around boolean functions that determines a relationship
between an actor and a resourc.

Resource can essentially be any entity in an application.
Actors represents any entity that, in an application, can act upon a resource.
"""

import inspect
from typing import Any, Callable, ClassVar, Generic, Protocol, TypeVar, cast

from entitled import exceptions

Resource = TypeVar("Resource", contravariant=True)


class SyncRule(Protocol[Resource]):
    """Defines valid functions for rules"""

    def __call__(
        self,
        actor: Any,
        resource: Resource | type[Resource],
        context: dict[str, Any] | None = None,
    ) -> bool: ...


class AsyncRule(Protocol[Resource]):
    """Defines valid functions for rules"""

    async def __call__(
        self,
        actor: Any,
        resource: Resource | type[Resource],
        context: dict[str, Any] | None = None,
    ) -> bool: ...


RuleProtocol = SyncRule[Resource] | AsyncRule[Resource]


async def handle_rule(
    func: AsyncRule[Resource] | SyncRule[Resource],
    actor: Any,
    resource: Resource | type[Resource],
    context: dict[str, Any] | None = None,
):
    if inspect.iscoroutinefunction(func):
        fn = cast(AsyncRule[Resource], func)
        return await fn(actor, resource, context)
    else:
        fn = cast(SyncRule[Resource], func)
        return fn(actor, resource, context)


class Rule(Generic[Resource]):
    """Base class for rules

    Args:
        name (str): The name given to this rule.
        rule_function (Callable): The underlying boolean function.
    """

    _registry: ClassVar[dict[str, "Rule[Any]"]] = {}

    @classmethod
    def clear_registry(cls) -> None:
        cls._registry = {}

    @classmethod
    def get_rule(cls, name: str) -> "Rule[Resource] | None":
        return Rule._registry[name] if name in Rule._registry else None

    def __init__(self, name: str, rule_function: RuleProtocol[Resource]):
        self.name = name
        self.rule = rule_function
        self.__register()

    def __register(self) -> None:
        if self.name in Rule._registry:
            print(f"A rule identified by '{self.name}' already exists.")
            return

        Rule._registry[self.name] = self

    async def __call__(
        self,
        actor: Any,
        resource: Resource | type[Resource],
        context: dict[str, Any] | None = None,
    ) -> bool:
        if not context:
            context = {}
        return await handle_rule(self.rule, actor, resource, context)

    async def authorize(
        self,
        actor: Any,
        resource: Resource | type[Resource],
        context: dict[str, Any] | None = None,
    ) -> bool:
        if not await self(actor, resource, context):
            raise exceptions.AuthorizationException("Unauthorized")
        return True

    async def allows(
        self,
        actor: Any,
        resource: Resource | type[Resource],
        context: dict[str, Any] | None = None,
    ) -> bool:
        return await self(actor, resource, context)


def rule(name: str) -> Callable[[RuleProtocol[Resource]], RuleProtocol[Resource]]:
    def wrapped(func: RuleProtocol[Resource]):
        _ = Rule[Resource](name, func)
        return func

    return wrapped
