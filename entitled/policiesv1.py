from typing import Any

from entitled.rulesv1 import Actor, Rule, RuleProto


class Client:
    def __init__(self):
        self._rule_registry: dict[str, Rule[Any]] = {}

    def define_rule(self, name: str, callable: RuleProto[Actor]) -> Rule[Actor]:
        rule = Rule(name, callable)
        self._rule_registry[rule.name] = rule
        return rule

    def allows(self, name: str, actor: Actor, *args: Any, **kwargs: Any):
        if name in self._rule_registry:
            return self._rule_registry[name].allows(actor, *args, **kwargs)
        return False

    def allows(self, name: str, actor: Actor, *args: Any, **kwargs: Any):
        if name in self._rule_registry:
            return self._rule_registry[name].allows(actor, *args, **kwargs)
        return False

    def denies()
