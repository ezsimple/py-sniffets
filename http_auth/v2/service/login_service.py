from fastapi import HTTPException
from passlib.context import CryptContext
from core.config import settings
from jose import jwt
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def login(username: str, password: str):
    if username != settings.USERNAME or not verify_password(password, settings.PASSWORD):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # JWT 토큰 생성
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_EXPIRATION)
    token = jwt.encode({"sub": username, "exp": expiration}, settings.JWT_SECRET, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer"}
