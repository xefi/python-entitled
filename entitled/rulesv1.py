from typing import Any, ClassVar, Protocol, TypeVar


Actor = TypeVar("Actor", contravariant=True)


class RuleProto(Protocol[Actor]):
    async def __call__(self, actor: Actor, *args: Any, **kwargs: Any) -> bool: ...


class Rule[Actor]:
    _registry: ClassVar[dict[str, RuleProto[Any]]] = {}
    _before_callback: RuleProto[Any] | None = None

    @classmethod
    def define(cls, name: str, closure: RuleProto[Actor]) -> None:
        cls._registry[name] = closure

    @classmethod
    def before(cls, rule: RuleProto[Actor] | None):
        cls._before_callback = rule

    @classmethod
    async def allows(
        cls,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        if name in cls._registry:
            return await cls._registry[name](actor, args, kwargs)

        return False

    @classmethod
    async def denies(
        cls,
        name: str,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await cls.allows(name, actor)

    @classmethod
    async def any(
        cls,
        names: list[str],
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return any([await cls.allows(name, actor, args, kwargs) for name in names])

    @classmethod
    async def none(
        cls,
        names: list[str],
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await cls.any(names, actor, args, kwargs)
