from passlib.context import CryptContext

import os
import jwt
import time

SECRET_KEY = os.getenv("JWT_SECRET", "dev_secret_key",)
ALGO = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + 3600
        }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGO)

def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGO])

