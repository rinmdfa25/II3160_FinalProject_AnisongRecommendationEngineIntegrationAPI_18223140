from passlib.context import CryptContext
import os
import jwt
import time

SECRET_KEY = os.getenv("JWT_SECRET", "devsecret")
ALGO = "HS256"

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd.hash(password)

def verify_password(plain, hashed):
    return pwd.verify(plain, hashed)

def create_token(user_id):
    now = int(time.time())
    payload = {
    "sub": str(user_id),
    "iat": now,
    "exp": now + 3600,
    "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def create_refresh_token(user_id):
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + 604800, # 7 hari
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload