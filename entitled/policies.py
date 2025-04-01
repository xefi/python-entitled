from typing import Any
from entitled.rules import RuleProto


class Policy[T]:
    def rule(self):
        def wrapped(func: RuleProto[Any]):
            func._is_rule = True
            return func

        return wrapped
