import factory

from tests.data import models


class TenantFactory(factory.Factory):
    class Meta:
        model = models.Tenant

    name = factory.Faker("company")


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    name = factory.Faker("name")
