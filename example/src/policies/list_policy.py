from typing import Any

import entitled

from src.models import TodoList, User

list_policy = entitled.Policy[TodoList]()


@list_policy.rule("read")
def can_see_list(
    actor: User, resource: TodoList, context: dict[str, Any] | None = None
) -> bool:
    return resource.owner == actor or actor in resource.watchers


@list_policy.rule("edit")
def can_edit_list(
    actor: User, resource: TodoList, context: dict[str, Any] | None = None
) -> bool:
    return resource.owner == actor
