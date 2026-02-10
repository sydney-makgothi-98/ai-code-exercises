"""
Simple FastAPI to-do list app (in-memory storage).
Run with: uvicorn "my api:app" --reload
"""

from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="To-Do API", version="1.0.0")


class TodoCreate(BaseModel):
	title: str = Field(..., min_length=1, max_length=100)
	description: Optional[str] = Field(None, max_length=500)
	due_date: date


class Todo(TodoCreate):
	id: int
	completed: bool = False


_todos: dict[int, Todo] = {}
_next_id = 1


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoCreate) -> Todo:
	global _next_id
	todo = Todo(id=_next_id, **payload.model_dump())
	_todos[_next_id] = todo
	_next_id += 1
	return todo


@app.get("/todos", response_model=list[Todo])
def list_todos(
	status: Optional[str] = Query(
		None, pattern="^(completed|pending)$", description="Filter by status"
	)
) -> list[Todo]:
	items = list(_todos.values())
	if status == "completed":
		return [todo for todo in items if todo.completed]
	if status == "pending":
		return [todo for todo in items if not todo.completed]
	return items


@app.patch("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: int) -> Todo:
	todo = _todos.get(todo_id)
	if not todo:
		raise HTTPException(status_code=404, detail="To-do item not found.")
	if not todo.completed:
		todo.completed = True
		_todos[todo_id] = todo
	return todo


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
	if todo_id not in _todos:
		raise HTTPException(status_code=404, detail="To-do item not found.")
	del _todos[todo_id]
