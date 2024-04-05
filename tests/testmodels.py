import dataclasses
import typing

from entitled.roles import Role


@dataclasses.dataclass
class Tenant:
    name: str


@dataclasses.dataclass
class User:
    name: str
    tenant: Tenant
    roles: set[Role] = dataclasses.field(default_factory=set)


@dataclasses.dataclass
class Node:
    name: str
    owner: User
    tenant: Tenant
    parent: typing.Optional["Node"] = None
