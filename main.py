from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app import pass_db_url, pass_jwt_secret, auth, task

jwt_secret = os.getenv("JWT_SECRET")
pass_jwt_secret(jwt_secret) if jwt_secret else SystemExit("JWT_SECRET is not set")

db_url = os.getenv("DB_URL")
pass_db_url(db_url) if db_url else SystemExit("DB_URL is not set")

app = FastAPI(title="task-tracker")

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_credentials = True,
  allow_headers = ["*"],
  allow_methods = ["*"],
)

app.include_router(auth, prefix="/auth", tags=["Authentication and Account Management"])

app.include_router(task, prefix="/task", tags=["Task Management"])
