from fastapi import Depends, HTTPException
from fastapi import Cookie, Request
import jwt
from sqlmodel import Session, select
from .models import User, get_session



class CookieJWT:
  def __init__(self, jwt_secret):
    self.jwt_secret = jwt_secret

  def session_cookie_from_username(self, username: str):
    return jwt.encode({"username": username}, self.jwt_secret, algorithm="HS256")

  def username_from_session_cookie(self, session_cookie: str):
    return jwt.decode(session_cookie, self.jwt_secret, algorithms=["HS256"]).get("username")



def pass_jwt_secret(jwt_secret):
  global jwt_cookie
  jwt_cookie = CookieJWT(jwt_secret)

def get_jwt_cookie():
  global jwt_cookie
  yield jwt_cookie



def auth_middleware(request: Request, session: Session = Depends(get_session), session_cookie: str | None = Cookie(default=None)):
  if not session_cookie:
    raise HTTPException(status_code=401, detail="Login to access the tasks")
  
  try:
    global jwt_cookie
    request.state.username = jwt_cookie.username_from_session_cookie(session_cookie)
  except:
    raise HTTPException(status_code=401, details="Session Expired or Invalid Login credentials, Login again")

  request.state.user = session.exec(select(User).where(User.username == request.state.username)).first()
  if not request.state.user:
    raise HTTPException(status_code=401, detail="User not found or not allowed")

