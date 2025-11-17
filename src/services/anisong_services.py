import httpx
from fastapi import Query
from typing import Optional 

BASE_URL = "https://api.animethemes.moe"

async def fetch_anisong_list(theme_type: str, limit: int = 25):
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

async def fetch_anisong_name(name: str, limit: int = 5):
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
        
async def fetch_anisong_criteria(
    year: Optional[int] = None,
    season: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 25
):
    base_url = f"{BASE_URL}/anime"
    
    params = {
        "include": "animethemes.song.artists,animethemes.animethemeentries.videos",
        "page[size]": limit
    }
    
    criteria_filters = {}
    if year:
        criteria_filters["year"] = year
    if season:
        criteria_filters["season"] = season
    if genre:
        criteria_filters["genre"] = genre
        
    criteria_filter_str = "&".join(criteria_filters)
    
    if criteria_filters:
        params["filter"] = criteria_filters
        
    url = (
        f"{base_url}"
        f"?{criteria_filter_str}"
        f"&include=animethemes.song.artists,animethemes.animethemeentries.videos"
        f"&page[size]={limit}"
    )    
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
    anime_songs = []
    for anime in data.get("anime", []):
        anime_name = anime.get("name")
        for theme in anime.get("animethemes", []):
            song = theme.get("song", {})
            anime_songs.append({
                "anime": anime_name,
                "song_title": song.get("title"),
                "artists" : [a.get("name") for a in song.get("artists", [])],
                "theme_type": theme.get("type")
            })  
    return anime_songs 