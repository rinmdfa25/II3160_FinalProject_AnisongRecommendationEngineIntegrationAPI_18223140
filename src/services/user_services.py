from sqlmodel import Session, select
from src.models.user_model import User
from src.services.auth_services import hash_password

def get_user_by_username(session: Session, username: str):
    return session.exec(
        select(User).where(User.username == username)
    ).first()

def create_user(session: Session, username: str, password: str):
    hashed = hash_password(password)
    user = User(username=username, password_hash=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
