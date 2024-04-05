"""Module for roles management.

Still *very* WIP.
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class Role:
    """The base Role model"""

    name: str
