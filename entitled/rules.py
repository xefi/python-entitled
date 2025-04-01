from typing import Any, Literal, Protocol, TypeVar

from entitled.exceptions import AuthorizationException
from entitled.response import Err, Ok, Response


Actor = TypeVar("Actor", contravariant=True)


class RuleProto(Protocol[Actor]):
    async def __call__(
        self, actor: Actor, *args: Any, **kwargs: Any
    ) -> Response | bool: ...


class Rule[Actor]:
    name: str
    callable: RuleProto[Actor]

    def __init__(self, name: str, callable: RuleProto[Actor]) -> None:
        self.name = name
        self.callable = callable

    async def __call__(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> Response | bool:
        return await self.callable(actor, *args, **kwargs)

    async def inspect(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        result = await self(actor, *args, **kwargs)
        match result:
            case True:
                return Ok()
            case False:
                return Err("Unauthorized")
            case _:
                return result

    async def allows(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return (await self.inspect(actor, *args, **kwargs)).allowed()

    async def denies(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await self.allows(actor, *args, **kwargs)

    async def authorize(
        self,
        actor: Actor,
        *args: Any,
        **kwargs: Any,
    ) -> Literal[True]:
        res = await self.inspect(actor, *args, **kwargs)
        if not res.allowed():
            raise AuthorizationException(res.message())
        return True
