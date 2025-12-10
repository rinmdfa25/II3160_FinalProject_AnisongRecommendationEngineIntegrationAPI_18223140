import httpx
from fastapi import Query
from typing import Optional
from sqlmodel import Session, select
from src.models.anisong_model import AnisongDB
from src.models.user_model import UserHistory
from src.services.youtube_services import search_youtube
from src.services.spotify_services import search_spotify
import logging
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://api.animethemes.moe"

async def fetch_anisong_list(theme_type: str, limit: int = 25):
    if not theme_type in ["OP", "ED", "INS"]:
        return []
    
    url = (
        f"{BASE_URL}/animetheme?"
        f"filter[type]={theme_type}"
        f"&sort=-anime.year"
        f"&page[size]={limit}"
        f"&include=anime,animethemeentries,song.artists"
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    anime_context_only = []
    for item in data.get("animethemes", []):
        anime = item.get("anime", {})
        anime_name = anime.get("name")

        song = item.get("song", {})
        song_title = song.get("title")
        artists = [a.get("name") for a in song.get("artists", [])]

        anime_context_only.append({
            "anime": anime_name,
            "song_title": song_title,
            "artists": artists,
            "theme_type": item.get("type")
        })
    return anime_context_only

async def fetch_anisong_name(name: str, limit: int = 25):   
    url = (
        f"{BASE_URL}/anime?"
        f"filter[name]={name}"
        f"&include=animethemes.song.artists,animethemes.animethemeentries.videos"
        f"&limit={limit}"
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
    anime_names = []
    for anime in data.get("anime", []):
        anime_name = anime.get("name")
        for theme in anime.get("animethemes", []):
            song = theme.get("song", {})
            anime_names.append({
                "anime": anime_name,
                "song_title": song.get("title"),
                "artists": [a.get("name") for a in song.get("artists", [])],
                "theme_type": theme.get("type")
            })
    
    return anime_names     

async def fetch_anisong_artist(artist: str, limit: int = 25):
    url = (
    f"{BASE_URL}/artist?"
    f"filter[name]={artist}"
    f"&include=songs.animethemes.animethemeentries.videos,songs.animethemes.anime"
    f"&limit={limit}"
    )
  
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    songs = []

    for art in data.get("artists", []):
        for song in art.get("songs", []):
            title = song.get("title")
            artist_name = art.get("name")

            for theme in song.get("animethemes", []):
                anime = theme.get("anime") or {}
                anime_name = anime.get("name")
                year = anime.get("year")
                season = anime.get("season")

                songs.append({
                    "anime": anime_name,
                    "song_title": title,
                    "artists": [artist_name],
                    "theme_type": theme.get("type"),
                    "year": year,
                    "season": season
                })

    return songs


async def fetch_anisong_criteria(
    year: Optional[int] = None,
    season: Optional[str] = None,
    limit: int = 25
):
    base_url = f"{BASE_URL}/anime"
    
    params = {
        "include": "animethemes.song.artists",
        "page[size]": limit
    }
    
    if year:
        params["filter[year]"] = year
    if season == "winter" or season == "spring" or season == "summer" or season == "fall":
        params["filter[season]"] = season
           
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
    anime_songs = []
    for anime in data.get("anime", []):
        anime_name = anime.get("name")
        for theme in anime.get("animethemes", []):
            song = theme.get("song") or {}
            anime_songs.append({
                "anime": anime_name,
                "song_title": song.get("title") or "",
                "artists" : [a.get("name") for a in song.get("artists", [])],
                "theme_type": theme.get("type")
            })  
    return anime_songs 

def get_anisong_by_title_and_artist(session: Session, title: str, artist: str):
    return session.exec(
        select(AnisongDB).where(
            AnisongDB.title == title,
            AnisongDB.artist == artist
        )
    ).first()
    
def save_anisong(session: Session, title: str, artist: str, anime: str, spotify_url: str, popularity: int, youtube_url: str):
    exists = get_anisong_by_title_and_artist(session, title, artist)
    if exists:
        return exists
    
    song = AnisongDB(
        title=title,
        artist=artist,
        anime=anime,
        spotify_url=spotify_url,
        spotify_popularity=popularity,
        youtube_url=youtube_url
    )
    
    session.add(song)
    session.commit()
    session.refresh(song)
    return song

async def save_user_history(session: Session, user_id: int, song_id: int, score: float = 1.0):
    history = UserHistory(user_id=user_id, song_id=song_id, score=score)
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


async def resolve_anisong(raw):
    title = raw.get("song_title")
    artists = raw.get("artists", [])
    anime = raw.get("anime")
    
    main_artists = artists[0] if artists else ""
    
    youtube = await search_youtube(f"{title} {anime}")
    spotify = await search_spotify(title, main_artists)
    
    return {
        "anime": anime,
        "song_title": title,
        "artists": artists,
        "youtube_url": youtube,
        "spotify_url": spotify
    }
    
async def search_and_resolve_anisong(q: list[str], session: Session, user_id: int, limit: int = 15):
    logging.info(f"Query: {q}, Limit: {limit}")
    songs = []
    
    for query in q:    
        try:
            result = await fetch_anisong_list(query, limit =20)
            logging.info(f"fetch_anisong_list returned {len(result)} items")
        except httpx.HTTPStatusError as e:
            logging.warning(f"fetch_anisong_list error: {e}")
            result = []
            
        if not result:
            try:
                result = await fetch_anisong_name(query, limit =20)
                logging.info(f"fetch_anisong_name returned {len(result)} items")
            except httpx.HTTPStatusError as e:
                logging.warning(f"fetch_anisong_name error: {e}")
                result = []
        if not result:
            try:
                result = await fetch_anisong_artist(query, limit =20)
                logging.info(f"fetch_anisong_artist returned {len(result)} items")
            except httpx.HTTPStatusError as e:
                logging.warning(f"fetch_anisong_artist error: {e}")
                result = []
        if not result:
            if query.isdigit():
                year = int(query)
                season = None
            elif query.lower() in ["winter", "spring", "summer", "fall"]:
                season = query.lower()
                year = None
            else:
                year = int(query)
                season = str(query.lower())
            try:
                result = await fetch_anisong_criteria(year=year, season=season, limit=20)
                logging.info(f"fetch_anisong_criteria returned {len(result)} items")
            except httpx.HTTPStatusError as e:
                logging.warning(f"fetch_anisong_criteria error: {e}")
                result = []
        if not result:
            result = []
        
    for raw in result:
        resolved = await resolve_anisong(raw)
        logging.info(f"Resolved song: {resolved}")
        songs.append(resolved)

        title = resolved["song_title"]
        artist = resolved["artists"][0] if resolved["artists"] else "Unknown"
        anime = resolved["anime"]
        spotify_data = resolved["spotify_url"]
        if isinstance(spotify_data, dict):
            spotify_url = spotify_data.get("spotify_url")
            popularity = spotify_data.get("popularity", 0)
        else:
            spotify_url = spotify_data
            popularity = 0

        song = save_anisong(
            session=session,
            title=title,
            artist=artist,
            anime=anime,
            spotify_url=spotify_url,
            popularity=popularity,
            youtube_url=resolved["youtube_url"]
        )

        await save_user_history(session, user_id, song.id)

    return songs

