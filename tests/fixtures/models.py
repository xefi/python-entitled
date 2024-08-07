import dataclasses


@dataclasses.dataclass
class Tenant:
    name: str


@dataclasses.dataclass
class User:
    name: str
    tenant: Tenant
    roles: set[str]


@dataclasses.dataclass
class Resource:
    name: str
    owner: User
    tenant: Tenant
