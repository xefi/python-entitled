"""Centralization of all decision-making processes on a single decision point"""

import importlib.util
import pathlib
import types
from typing import Any

from entitled import policies


class Client:
    "The Client class for decision-making centralization."

    def __init__(self, base_path: str | None = None):
        self._policy_registrar: dict[type, policies.Policy[Any]] = {}
        self._load_path = None
        if base_path:
            self._load_path = pathlib.Path(base_path)
            self.load_policies_from_path(self._load_path)

    def authorize(
        self,
        action: str,
        actor: Any,
        resource: Any,
        context: dict[str, Any] | None = None,
    ) -> bool:
        policy = self._policy_lookup(resource)
        return policy.authorize(action, actor, resource, context)

    def allows(
        self,
        action: str,
        actor: Any,
        resource: Any,
        context: dict[str, Any] | None = None,
    ) -> bool:
        policy = self._policy_lookup(resource)
        return policy.allows(action, actor, resource, context)

    def grants(
        self,
        actor: Any,
        resource: Any,
        context: dict[str, Any] | None = None,
    ) -> dict[Any, bool]:
        policy = self._policy_lookup(resource)
        return policy.grants(actor, resource, context)

    def register(self, policy: policies.Policy[Any]):
        if hasattr(policy, "__orig_class__"):
            resource_type = getattr(policy, "__orig_class__").__args__[0]
            if resource_type not in self._policy_registrar:
                self._policy_registrar[resource_type] = policy
            else:
                raise ValueError(
                    "A policy is already registered for this resource type"
                )
        else:
            raise AttributeError(f"Policy {policy} is incorrectly defined")

    def reload_registrar(self):
        if self._load_path is not None:
            self.load_policies_from_path(self._load_path)

    def load_policies_from_path(self, path: pathlib.Path):
        for file_path in path.glob("*.py"):
            print(file_path)
            mod_name = file_path.stem
            full_module_name = ".".join(file_path.parts[:-1] + (mod_name,))
            spec = importlib.util.spec_from_file_location(full_module_name, file_path)
            if spec:
                module = importlib.util.module_from_spec(spec)
                if spec.loader:
                    try:
                        spec.loader.exec_module(module)
                    except Exception as e:
                        raise e

                    self._register_from_module(module)

    def _register_from_module(self, module: types.ModuleType):
        for attribute_name in dir(module):
            attr = getattr(module, attribute_name)
            if isinstance(attr, policies.Policy):
                try:
                    self.register(attr)
                except (ValueError, AttributeError):
                    pass

    def _policy_lookup(self, resource: Any) -> policies.Policy[Any]:
        lookup_key = resource if isinstance(resource, type) else type(resource)

        if lookup_key not in self._policy_registrar:
            raise ValueError("No policy registered for this resource type")

        return self._policy_registrar[lookup_key]
