from passlib.context import CryptContext

import os
import jwt
import time

SECRET_KEY = os.getenv("JWT_SECRET")
ALGO = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(user_id):
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + 3600,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload

