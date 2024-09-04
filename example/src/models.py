import pydantic


class User(pydantic.BaseModel):
    email: pydantic.EmailStr


class Task(pydantic.BaseModel):
    title: str
    description: str = ""
    done: bool = False
    parent_list: "TodoList"


class TaskCreateSchema(pydantic.BaseModel):
    title: str
    description: str = ""


class TodoList(pydantic.BaseModel):
    id: int
    title: str
    tasks: list[Task] = []
    owner: User
    watchers: list[User] = []


class ListsRegistry(pydantic.BaseModel):
    max_id: int = 0
    lists: dict[int, TodoList] = {}

    def get(self, id: int) -> TodoList | None:
        return self.lists.get(id)

    def add(self, list: TodoList):
        if list.id not in self.lists.keys():
            self.lists[list.id] = list
            self.max_id = max(self.max_id, list.id)
