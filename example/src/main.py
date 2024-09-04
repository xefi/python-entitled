import entitled
from fastapi import FastAPI, HTTPException, status
import pydantic

from src import models


users: dict[pydantic.EmailStr, models.User] = {}
lists = models.ListsRegistry()

auth_client = entitled.Client("entitled_example/policies")

app = FastAPI()


@app.post("/users", tags=["users"])
async def create_user(email: pydantic.EmailStr):
    if email not in users.keys():
        new_user = models.User(email=email)
        users[email] = new_user
        return new_user


@app.post("/lists", tags=["lists"])
async def create_list(list_title: str, current_user: str):
    user = users.get(current_user)
    print(user)
    if user:
        new_list = models.TodoList(id=lists.max_id + 1, title=list_title, owner=user)
        lists.add(new_list)
        return new_list
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@app.get("/lists/{id}", tags=["lists"])
async def get_list(id: int, current_user: str):
    user = users.get(current_user)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    result = lists.get(id)

    if not auth_client.allows("read", user, result):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return result


@app.post("/lists/{id}/tasks", tags=["tasks"])
async def add_task(id: int, current_user: str, task_data: models.TaskCreateSchema):
    user = users.get(current_user)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    parent_list = lists.get(id)

    if parent_list is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if not auth_client.allows("edit", user, parent_list):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    new_task = models.Task(
        title=task_data.title,
        description=task_data.description,
        parent_list=parent_list,
    )

    return new_task


@app.get("/lists/{id}/permissions", tags=["lists"])
async def inspect_perms(id: int, current_user: str):
    user = users.get(current_user)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    target_list = lists.get(id)

    if target_list is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return auth_client.grants(user, target_list)
