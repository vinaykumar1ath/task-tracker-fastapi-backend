from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from fastapi import Request
from typing import List, Optional
from .jwt_auth_helpers import auth_middleware
from .models import Task, TaskCreate, TaskUpdate, get_session

task = APIRouter(dependencies=[Depends(auth_middleware)])

@task.post("/")
def create_task(task_data: TaskCreate, request: Request, session: Session = Depends(get_session)):
  task = Task.model_validate(task_data)
  task.user_id = request.state.user.id

  try:
    session.add(task)
    session.commit()
    session.refresh(task)
  except:
    raise HTTPException(status_code=404, detail="Cannot create task")

  return {"msg": "Task Created"}

@task.get("/", response_model=List[Task])
def get_task(request: Request, id: Optional[int]=None, title: Optional[str]=None, done: Optional[bool]=None, session: Session = Depends(get_session)):
  
  query = select(Task).where(Task.user_id == request.state.user.id)
  if id:
    query = query.where(Task.id == id)
  if title:
    query = query.where(Task.title == title)
  if done is not None:
    query = query.where(Task.done == done)

  tasks = session.exec(query).all()
  return tasks

@task.patch("/", response_model=Task)
def write_task(request: Request, task_id: int, task_data: TaskUpdate, session: Session = Depends(get_session)):
  if not task_id:
    raise HTTPException(status_code=404, detail="Task ID is required to update tasks")
  
  task = session.get(Task, task_id)
  if not task:
    raise HTTPException(status_code=404, detail="Task with the Task ID not found")

  task_updates = task_data.model_dump(exclude_unset=True)
  for key, value in task_updates.items():
    setattr(task, key, value)

  session.add(task)
  session.commit()
  session.refresh(task)

  return task

@task.delete("/")
def delete_task(requst: Request, task_id: int, session: Session = Depends(get_session)):
  
  if not task_id:
    raise HTTPException(status_code=404, detail="Task ID is required to delete tasks")
  
  task = session.get(Task, task_id)
  if not task:
    raise HTTPException(status_code=404, detail="Task with the Task ID not found")

  session.delete(task)
  session.commit()

  return {"msg": "Task Deleted"}
