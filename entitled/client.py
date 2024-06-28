"""Centralization of all decision-making processes on a single decision point"""

import importlib.util
import pathlib
import types
import typing

from entitled import policies


class Client:
    "The Client class for decision-making centralization."

    def __init__(self, base_path="policies"):
        self._policy_registrar: dict[typing.Type, policies.Policy] = {}
        self._load_path = pathlib.Path(base_path)
        self.load_policies_from_path(self._load_path)

    def authorize(self, actor, action, resource, context: dict | None = None):
        policy = self._policy_lookup(resource)
        return policy.authorize(actor, action, resource, context)

    def allows(self, actor, action, resource, context: dict | None = None) -> bool:
        policy = self._policy_lookup(resource)
        return policy.allows(actor, action, resource, context)

    def actions(self, actor, resource, context: dict | None = None):
        policy = self._policy_lookup(resource)
        return policy.grants(actor, resource, context)

    def register_policy(self, policy: policies.Policy):
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
        self.load_policies_from_path(self._load_path)

    def load_policies_from_path(self, path: pathlib.Path):
        for file_path in path.glob("*.py"):
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
                    self.register_policy(attr)
                except (ValueError, AttributeError):
                    pass

    def _policy_lookup(self, resource) -> policies.Policy:
        if type(resource) not in self._policy_registrar:
            raise ValueError("No policy registered for this resource type")

        return self._policy_registrar[type(resource)]
