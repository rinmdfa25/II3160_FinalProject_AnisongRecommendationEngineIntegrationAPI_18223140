from fastapi import APIRouter, Depends
from sqlmodel import Session
from src.utils.sqlite import get_session
from src.services.preferences_service import get_user_preferences, add_preference
from src.routers.auth import get_current_user

router = APIRouter(prefix="/preferences")

@router.get("/")
def list_preferences(
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    return get_user_preferences(session, int(user_id))

@router.post("/")
def create_preference(
    tag: str,
    weight: float, 
    session: Session = Depends(get_session),
    user_id: str = Depends(get_current_user)
):
    return add_preference(session, int(user_id), tag, weight)
