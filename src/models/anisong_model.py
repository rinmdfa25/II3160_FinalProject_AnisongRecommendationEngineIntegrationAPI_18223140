from typing import Optional

from sqlmodel import Field, SQLModel
class AnisongDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    artist: str
    anime: Optional[str]
    spotify_url: Optional[str]
    spotify_popularity: Optional[int]
    youtube_url: Optional[str]