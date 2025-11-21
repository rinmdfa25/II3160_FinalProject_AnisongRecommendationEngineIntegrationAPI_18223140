from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from src.utils.database import get_session
from src.services.user_services import get_user_by_username, create_user
from src.services.auth_services import verify_password, create_token, decode_token
from src.models.request_model import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth")
oauth = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    user = get_user_by_username(session, data.username)
    
    if user:
        raise HTTPException(status_code=400, detail="username already exists")

    new_user = create_user(session, data.username, data.password)

    return {"id": new_user.id, "username": new_user.username}


@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_username(session, data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Username")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Password")

    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth)):
    try:
        payload = decode_token(token)
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired Token")
