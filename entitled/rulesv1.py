from typing import Any, Protocol, TypeVar


Actor = TypeVar("Actor", contravariant=True)


class RuleProto(Protocol[Actor]):
    async def __call__(
        self, actor: Actor, *args: Any, **kwargs: Any
    ) -> bool | None: ...


class Rule[Actor]:
    def __init__(self, name: str, callable: RuleProto[Actor]) -> None:
        self.name = name
        self.callable = callable
        self._before_callbacks: list[RuleProto[Actor]] = []

    def before(self, *rule: RuleProto[Actor]):
        self._before_callbacks = list(rule)

    async def allows(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        response = await self.callable(actor, args, kwargs)
        return response if response is not None else False

    async def denies(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await self.allows(actor)
