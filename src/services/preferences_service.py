from sqlmodel import Session, select
from src.models.user_model import UserPreference

def get_user_preferences(session: Session, user_id: int):
    return session.exec(
        select(UserPreference).where(UserPreference.user_id == user_id)
    ).all()
    
def add_preference(session: Session, user_id: int, tag: str, weight: float):
    pref = UserPreference(user_id=user_id, tag=tag, weight=weight)
    session.add(pref)
    session.commit()
    session.refresh(pref)
    return pref

def update_preference_from_history(session: Session, user_id: int, artist: str, anime: str):
    tags = [artist, anime]
    for tag in tags:
        pref = session.exec(
            select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.tag == tag
            )
        ).first()
        if pref:
            pref.weight += 1
        else:
            pref = UserPreference(
                user_id=user_id,
                tag=tag,
                weight=1
            )
            session.add(pref)
    session.commit()