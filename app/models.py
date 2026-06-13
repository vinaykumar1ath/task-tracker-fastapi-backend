from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import create_engine, Session
from typing import Optional, List
from pydantic import EmailStr


class User(SQLModel, table=True):
  id: Optional[int] = Field(index=True, primary_key=True, unique=True, default=None)
  username: str = Field(max_length=25, index=True, unique=True)
  email: Optional[EmailStr] = Field(default=None)
  password: str

  tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
  id: Optional[int] = Field(index=True, primary_key=True, unique=True, default=None)
  title: str = Field(index=True)
  description: str
  user_id: int = Field(foreign_key="user.id", default=None)
  done: Optional[bool] = Field(default=False)

  user: Optional[User] = Relationship(back_populates="tasks")


class TaskCreate(SQLModel):
  title: str
  description: str

class TaskUpdate(SQLModel):
  title: Optional[str] = Field(default=None)
  description: Optional[str] = Field(default=None)
  done: Optional[bool] = Field(default=None)

class UserData(SQLModel):
  username: str
  password: str
  email: Optional[EmailStr] = Field(default=None)



def get_session():
  global engine
  with Session(engine) as session:
    yield session

def pass_db_url(db_url):
  global engine
  engine = create_engine(db_url)
  SQLModel.metadata.create_all(engine)
