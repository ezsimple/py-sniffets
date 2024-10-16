from fastapi import HTTPException
from core.config import settings, pwd_context
from jose import jwt
import datetime

def verify_password(plain_password, hashed_password):
    print(f"Verifying password: {plain_password} with hash: {hashed_password}")
    result = pwd_context.verify(plain_password, hashed_password)
    print(result)
    return result

def get_password_hash(password):
    '''
    .env, db등에 패스워드 저장시 사용
    '''
    return pwd_context.hash(password)

async def login(username: str, password: str):
    hashed_password = settings.PASSWORD  # 데이터베이스에서 가져온 해시된 비밀번호
    if username != settings.USERNAME or not verify_password(password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # JWT 토큰 생성
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_EXPIRATION)
    token = jwt.encode({"sub": username, "exp": expiration}, settings.JWT_SECRET, algorithm="HS256")
    
    return {"access_token": token, "token_type": "bearer"}
