import dataclasses


@dataclasses.dataclass
class Tenant:
    name: str
    owner: "User | None" = None


@dataclasses.dataclass
class User:
    name: str
    tenant: Tenant | None = None
    roles: set[str] = dataclasses.field(default_factory=set)


@dataclasses.dataclass
class Resource:
    name: str
    owner: User
    tenant: Tenant
