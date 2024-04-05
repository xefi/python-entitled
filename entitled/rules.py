"""Basic building block of the Entitled library.

Rules are essentially wrappers around boolean functions that determines a relationship
between an actor and a resourc.

Resource can essentially be any entity in an application.
Actors represents any entity that, in an application, can act upon a resource.
"""

import typing

from entitled import exceptions

ResourceModel = typing.TypeVar("ResourceModel", contravariant=True)
ActorModel = typing.TypeVar("ActorModel", contravariant=True)


class Rule(typing.Generic[ActorModel, ResourceModel]):
    """Base class for rules

    Args:
        name (str): The name given to this rule.
        rule (Callable): The underlying boolean function.
    """

    def __init__(
        self, name: str, rule: typing.Callable[[ActorModel, ResourceModel, dict], bool]
    ):
        self.name = name
        self.rule = rule

    def __call__(
        self,
        actor: ActorModel,
        resource: ResourceModel,
        context: typing.Optional[dict] = None,
    ) -> bool:
        if not context:
            context = {}
        return self.rule(actor, resource, context)

    def __and__(self, rh_rule: "Rule[ActorModel, ResourceModel]"):
        return Rule(
            f"{self.name}&{rh_rule.name}",
            lambda actor, resource, context: (
                self(actor, resource, context) and rh_rule(actor, resource, context)
            ),
        )

    def __or__(self, rh_rule: "Rule[ActorModel, ResourceModel]"):
        return Rule(
            f"{self.name}|{rh_rule.name}",
            lambda actor, resource, context: (
                self(actor, resource, context) or rh_rule(actor, resource, context)
            ),
        )

    def authorize(
        self,
        actor: ActorModel,
        resource: ResourceModel,
        context: typing.Optional[dict] = None,
    ) -> bool:
        if not self(actor, resource, context):
            raise exceptions.AuthorizationException("Unauthorized")
        return True
