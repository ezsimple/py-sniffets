from pydantic import BaseModel
from datetime import datetime
from fastapi import Request, Response


class User(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class LoginMiddleWare:
    async def __call__(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return Response("Unauthorized", status_code=401)
        response = await call_next(request)
        return response