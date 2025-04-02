import inspect
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
        sig = inspect.signature(self.callable)
        args_count = len(
            [
                p
                for p in sig.parameters.values()
                if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        )
        valid_positionals = (actor,) + args[: args_count - 1]
        valid_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k in sig.parameters
            and sig.parameters[k].kind
            in (inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        }
        bound = sig.bind_partial(*valid_positionals, **valid_kwargs)

        return await self.callable(*bound.args, **bound.kwargs)

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
