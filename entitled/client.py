from importlib import util
from pathlib import Path
import types
from typing import Any, Literal

from entitled.exceptions import AuthorizationException
from entitled.policies import Policy
from entitled.response import Err, Response


class Client:
    load_path: Path | None = None
    _policy_registry: dict[type, Policy[Any]]

    def __init__(self, path: str | None = None):
        self._policy_registry = dict()
        if path is not None:
            self.load_path = Path(path)
            self.load_policies()

    def register_policy(self, policy: Policy[Any]):
        resource_type = getattr(policy, "__orig_class__").__args__[0]
        self._policy_registry[resource_type] = policy

    def load_policies(self, path: Path | None = None):
        path = path if path is not None else self.load_path
        if path is None:
            return
        for file in path.glob("*.py"):
            mod_name = file.stem
            full_mod_name = ".".join(file.parts[:-1] + (mod_name,))
            spec = util.spec_from_file_location(full_mod_name, file)
            if spec is not None:
                mod = util.module_from_spec(spec)
                if spec.loader:
                    try:
                        spec.loader.exec_module(mod)
                        self._register_from_module(mod)
                    except Exception as e:
                        raise e

    def _register_from_module(self, mod: types.ModuleType):
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if isinstance(attr, Policy):
                try:
                    self.register_policy(attr)
                except (ValueError, AttributeError):
                    pass

    def _resolve_policy(self, resource: Any) -> Policy[Any] | None:
        lookup_key = resource if isinstance(resource, type) else type(resource)
        policy = self._policy_registry.get(lookup_key, None)
        return policy

    async def inspect(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        policy = self._resolve_policy(resource)
        if policy is not None:
            return await policy.inspect(name, actor, resource, *args, **kwargs)
        return Err(f"No policy found with name '{name}'")

    async def allows(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return (await self.inspect(name, actor, resource, *args, **kwargs)).allowed()

    async def denies(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> bool:
        return not await self.allows(name, actor, resource, *args, **kwargs)

    async def authorize(
        self,
        name: str,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Literal[True]:
        result = await self.inspect(name, actor, resource, *args, **kwargs)
        if not result.allowed():
            raise AuthorizationException(result.message())
        return True

    async def grants(
        self,
        actor: Any,
        resource: Any,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, bool]:
        policy = self._resolve_policy(resource)
        if policy is None:
            return {}
        return await policy.grants(actor, resource, *args, **kwargs)
