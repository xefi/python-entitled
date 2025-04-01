import dataclasses


@dataclasses.dataclass
class Tenant:
    name: str
    owner: "User | None" = None


@dataclasses.dataclass
class User:
    name: str
    tenant: Tenant | None
    roles: set[str]


@dataclasses.dataclass
class Resource:
    name: str
    owner: User
    tenant: Tenant
