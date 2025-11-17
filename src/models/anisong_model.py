from pydantic import BaseModel
from typing import List, Optional, Literal

class Video(BaseModel):
    id: int
    resolution: Optional[str]
    link: Optional[str]
    audio: Optional[str]
    source: Optional[Literal["webm", "mp4"]]

class Artist(BaseModel):
    id: int
    name: str

class Song(BaseModel):
    id: int
    title: str
    artists: List[Artist]
    year: int
    normalized_name: Optional[str]
    spotify_url: Optional[str]
    youtube_search_url: Optional[str]

class ThemeMetadata(BaseModel):
    sequence: Optional[int]
    source: Optional[str]
    version: Optional[str]

class Theme(BaseModel):
    id: int
    anime_id: Optional[int]
    type: Optional[Literal["OP", "ED", "insert"]]
    sequence: Optional[int]
    song: Optional[Song]
    videos: List[Video]
    metadata: Optional[ThemeMetadata]

class AnimeMetadata(BaseModel):
    year: Optional[int]
    season: Optional[str]
    genres: Optional[List[str]]

class Anime(BaseModel):
    id: int
    title: str
    year: Optional[int]
    season: Optional[str]
    themes: List[Theme]
    metadata: Optional[AnimeMetadata]

class Anisong(BaseModel):
    song: Song
    spotify_url: Optional[str]
    youtube_search_url: Optional[str]
    normalized_name: Optional[str]
    themes_metadata: Optional[List[ThemeMetadata]]
    anime_metadata: Optional[AnimeMetadata]

