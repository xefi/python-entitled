import functools
from typing import Any, Callable


def rule(func: Callable[..., Any]):
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    setattr(wrapper, "_is_rule", True)
    return wrapper


class Policy[T]:
    pass
