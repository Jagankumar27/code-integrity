import hashlib, hmac, os, time
import jwt
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from .. import config
from ..database.db import get_db
from ..models.models import User

def hash_pw(pw, salt=None):
    salt = salt or os.urandom(8).hex()
    return salt + "$" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 60_000).hex()

def check_pw(pw, stored):
    salt = stored.split("$")[0]
    return hmac.compare_digest(hash_pw(pw, salt), stored)

def make_token(user):
    return jwt.encode({"sub": str(user.id), "exp": int(time.time()) + 8 * 3600}, config.SECRET_KEY, algorithm="HS256")

def current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    try:
        uid = int(jwt.decode(authorization[7:], config.SECRET_KEY, algorithms=["HS256"])["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, uid)
    if not user:
        raise HTTPException(401, "Unknown user")
    return user

def teacher_only(user: User = Depends(current_user)):
    if user.role != "teacher":
        raise HTTPException(403, "Teacher access required")
    return user
