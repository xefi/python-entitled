from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Ok:
    def allowed(self):
        return True

    def message(self):
        return None


@dataclass(frozen=True)
class Err:
    msg: str = ""

    def allowed(self):
        return False

    def message(self):
        return self.msg


Response = Ok | Err
