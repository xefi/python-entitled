![versions](https://img.shields.io/badge/python-3.12-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An authorization library for Python.

Aims to provide the tools to organize, enforce and audit your authorization layer as easily as possible, letting you focus on the essential part: the actual rules.

## Documentation

For the full documentation, go [here](https://python-entitled.xefi.com/)

## A sneak peek...

```py
from entitled import Policy, Client

# Some actors and resources of your application...
class User:
    def __init__(self, id: int, role: str):
        self.id: str = id
        self.role: str = role

class Resource:
    def __init__(self, id: int, user: User):
        self.id: str = id
        self.owner: User = user

my_policy = Policy[Resource]("resource") # Defining a policy for your resource

@my_policy.rule("edit")# Declaring a rule on the resource
def can_edit(
    actor: User, resource: Resource, context = None
        ) -> bool:
    return actor == resource.owner or actor.role == "admin"

client = Client()
client.register(my_policy) # Registering a policy

user1 = User(1, "user")
resource1 = Resource(1, user1)
if client.allows("edit", user1, resource1): # Using the client to make auth decisions
    ...
```
## Support us

<p><a href="https://www.xefi.com" target="_blank"><img src="https://raw.githubusercontent.com/xefi/art/main/support-landscape.svg" width="400"></a></p>

Since 1997, XEFI is a leader in IT performance support for small and medium-sized businesses through its nearly 200 local agencies based in France, Belgium, Switzerland and Spain.
A one-stop shop for IT, office automation, software, [digitalization](https://www.xefi.com/solutions-software/), print and cloud needs.
[Want to work with us ?](https://carriere.xefi.fr/metiers-software)
