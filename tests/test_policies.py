from entitled.policies import Policy
from entitled.rules import Rule
from tests.test_rules import can_edit, is_admin_on_node, is_member, is_owner
from tests.testmodels import Node, User

node_policy = Policy[Node](
    {
        "edit": [can_edit],
        "delete": [is_owner | is_admin_on_node],
        "view": [
            Rule[User, Node](
                "is_viewer",
                lambda actor, resource, context: is_member(actor, resource.tenant),
            )
        ],
    }
)
