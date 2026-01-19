from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Path, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


openapi_tags = [
    {"name": "System", "description": "Health and service metadata endpoints."},
    {"name": "Tasks", "description": "CRUD operations for to-do tasks."},
]


app = FastAPI(
    title="To-Do List API",
    description=(
        "A simple REST API for managing to-do tasks.\n\n"
        "Tasks include a title, optional description, and a completion status."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# Allow local dev + hosted preview URLs. Using wildcard keeps template simple.
# If you want stricter CORS, set allow_origins to your frontend URL(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskBase(BaseModel):
    """Shared fields for task create/update payloads."""

    title: str = Field(..., min_length=1, max_length=120, description="Short task title.")
    description: str = Field(
        default="",
        max_length=2000,
        description="Optional longer description of the task.",
    )
    completed: bool = Field(default=False, description="Whether the task is completed.")


class TaskCreate(TaskBase):
    """Request model for creating a task."""


class TaskUpdate(BaseModel):
    """Request model for updating a task (partial updates allowed)."""

    title: Optional[str] = Field(
        default=None, min_length=1, max_length=120, description="Short task title."
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional longer description of the task.",
    )
    completed: Optional[bool] = Field(
        default=None, description="Whether the task is completed."
    )


class Task(TaskBase):
    """Response model for tasks."""

    id: int = Field(..., description="Server-generated unique task id.")


# Simple in-memory persistence (sufficient for this template app).
_TASKS: Dict[int, Task] = {}
_NEXT_ID: int = 1


def _get_task_or_404(task_id: int) -> Task:
    """Internal helper to fetch a task or raise 404."""
    task = _TASKS.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Returns a basic health status message.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health_check() -> dict:
    """Health check endpoint.

    Returns:
        A simple JSON payload indicating the API is reachable.
    """
    return {"message": "Healthy"}


@app.get(
    "/tasks",
    response_model=List[Task],
    tags=["Tasks"],
    summary="List tasks",
    description="Returns all tasks ordered by id ascending.",
    operation_id="list_tasks",
)
# PUBLIC_INTERFACE
def list_tasks() -> List[Task]:
    """List all tasks.

    Returns:
        A list of tasks.
    """
    return [t for _, t in sorted(_TASKS.items(), key=lambda kv: kv[0])]


@app.post(
    "/tasks",
    response_model=Task,
    status_code=201,
    tags=["Tasks"],
    summary="Create task",
    description="Creates a new task and returns it.",
    operation_id="create_task",
)
# PUBLIC_INTERFACE
def create_task(payload: TaskCreate) -> Task:
    """Create a new task.

    Args:
        payload: The task fields.

    Returns:
        The created task with its assigned id.
    """
    global _NEXT_ID
    task = Task(id=_NEXT_ID, title=payload.title, description=payload.description, completed=payload.completed)
    _TASKS[_NEXT_ID] = task
    _NEXT_ID += 1
    return task


@app.get(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    summary="Get task",
    description="Fetch a single task by id.",
    operation_id="get_task",
)
# PUBLIC_INTERFACE
def get_task(
    task_id: int = Path(..., ge=1, description="Task id"),
) -> Task:
    """Get a task by id.

    Args:
        task_id: The task id.

    Returns:
        The task.

    Raises:
        HTTPException: 404 if not found.
    """
    return _get_task_or_404(task_id)


@app.put(
    "/tasks/{task_id}",
    response_model=Task,
    tags=["Tasks"],
    summary="Update task",
    description="Updates a task by id. Only provided fields are updated.",
    operation_id="update_task",
)
# PUBLIC_INTERFACE
def update_task(
    payload: TaskUpdate,
    task_id: int = Path(..., ge=1, description="Task id"),
) -> Task:
    """Update a task by id (partial update).

    Args:
        payload: Fields to update.
        task_id: The task id.

    Returns:
        The updated task.

    Raises:
        HTTPException: 404 if not found.
    """
    existing = _get_task_or_404(task_id)
    updated = existing.model_copy(
        update={k: v for k, v in payload.model_dump().items() if v is not None}
    )
    _TASKS[task_id] = updated
    return updated


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    response_class=Response,
    tags=["Tasks"],
    summary="Delete task",
    description="Deletes a task by id.",
    operation_id="delete_task",
)
# PUBLIC_INTERFACE
def delete_task(
    task_id: int = Path(..., ge=1, description="Task id"),
) -> Response:
    """Delete a task by id.

    Args:
        task_id: The task id.

    Returns:
        An empty 204 No Content response.

    Raises:
        HTTPException: 404 if not found.
    """
    _get_task_or_404(task_id)
    del _TASKS[task_id]
    return Response(status_code=204)
