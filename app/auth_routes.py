from fastapi import APIRouter, Depends, HTTPException
from fastapi import Cookie, Response, Request
from sqlmodel import Session, select
import bcrypt
from typing import Optional, List
from .models import User, UserData, get_session
from .jwt_auth_helpers import CookieJWT, get_jwt_cookie


auth = APIRouter()

@auth.post("/account")
def create_account(user_data: UserData, session: Session = Depends(get_session)):
  user_data = user_data.model_dump(exclude_unset=True)
  user = User.model_validate(user_data)
  user.password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

  try:
    session.add(user)
    session.commit()
  except:
    raise HTTPException(status_code=404, detail="username is not unique")

  return {"msg": "Account Created"}
    
@auth.delete("/account")
def delete_account(user_data: UserData, session: Session = Depends(get_session)):
  user = session.exec(select(User).where(User.username == user_data.username)).first()
  if not user:
    raise HTTPException(status_code=404, detail="user not found")
  if not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password.encode('utf-8')):
    raise HTTPException(status_code=404, detail="Incorrect Password")
  try:
    session.delete(user)
    session.commit()
  except:
    raise HTTPException(status_code=404, detail="Cannot delete User")

  return {"msg": "Account Deleted"}



@auth.post("/")
def login(user_data: UserData, response: Response, session: Session = Depends(get_session), jwt_cookie: CookieJWT = Depends(get_jwt_cookie)):
  
  user = session.exec(select(User).where(User.username == user_data.username)).first()
  if not user:
    raise HTTPException(status_code=401, detail="User not found")

  if not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password.encode('utf-8')):
    raise HTTPException(status_code=401, detail="Incorrect password")
  
  session_cookie = jwt_cookie.session_cookie_from_username(user.username)
  response.set_cookie(key="session_cookie", value=session_cookie, secure=False, httponly=True, max_age=76800, path="/")

  return {"msg": "Logged In"}

@auth.delete("/")
def logout(response: Response, session_cookie: str | None = Cookie(default=None), session: Session = Depends(get_session), jwt_cookie: CookieJWT = Depends(get_jwt_cookie)):

  try:
    username = jwt_cookie.username_from_session_cookie(session_cookie)
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
      raise HTTPException(status_code=401, detail="user not found")
  except:
    raise HTTPException(status_code=401, detail="Session expired or invalid session credentials")
  response.delete_cookie(key="session_cookie")

  return {"msg": "Logged Out"}

@auth.get("/")
def login_check(session_cookie: Optional[str] = Cookie(default=None), session: Session = Depends(get_session), jwt_cookie: CookieJWT = Depends(get_jwt_cookie)):

  try:
    username = jwt_cookie.username_from_session_cookie(session_cookie)
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
      raise HTTPException(status_code=404, detail="user not found")
    return {"msg": "Session is still alive, no need to login"}
  except:
    raise HTTPException(status_code=404, detail="Session expired or invalid session credentials, Login again")
