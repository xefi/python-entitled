import dataclasses


@dataclasses.dataclass
class Role:
    label: str


@dataclasses.dataclass
class Tenant:
    name: str


@dataclasses.dataclass
class User:
    name: str
    tenant: Tenant


@dataclasses.dataclass
class Node:
    name: str
    owner: User
    tenant: Tenant
    parent: "Node | None" = None
