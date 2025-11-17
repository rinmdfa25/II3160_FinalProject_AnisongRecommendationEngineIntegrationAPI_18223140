from fastapi import APIRouter, Query
from src.services.anisong_services import fetch_anisong_list, fetch_anisong_name, fetch_anisong_criteria
from src.services.youtube_service import search_youtube
from src.services.spotify_services import search_spotify
from typing import Optional
import asyncio


router = APIRouter(
    prefix="/anisong",
    tags=["anisong"]
)

@router.get("/themes")
async def search_anisongs_by_theme(theme_type: str = Query(..., regex="^(OP|ED|INS)$"), limit: int = Query(5, ge=1, le=50)):
    anisongs = await fetch_anisong_list(theme_type, limit)
    anisongs_results = []
    
    for song in anisongs:
        title = song["song_title"]
        artists = song["artists"]
        query_yt = f"{title} {song['anime']}"
    
        yt_task = search_youtube(query_yt)
        sp_task = search_spotify(title, artists)
        
        yt_url, sp_url = await asyncio.gather(yt_task, sp_task, return_exceptions=True)
        
        if isinstance(yt_url, Exception):
            yt_url = None
        if isinstance(sp_url, Exception):
            sp_url = None
            
        anisongs_results.append({
            "anime": song["anime"],
            "theme_type": song["theme_type"],
            "song_title": song["song_title"],
            "artists": song["artists"],
            "youtube_url": yt_url,
            "spotify_url": sp_url
        })
    
    return {"count": len(anisongs_results), "results": anisongs_results}

@router.get("/names")
async def search_anisong_by_name(
    name: str = Query(..., description="Name of anisong or anime title"),
    provider: str = Query("spotify", regex="^(spotify|youtube|both)$")
):

    anisong_names = await fetch_anisong_name(name=name, limit=5)    
    
    if not anisong_names:
        return {"count": 0, "results": []}
    
    anisongs_only = []
    for song in anisong_names:
        song_title = song.get("song_title", "")
        artists = song.get("artists", [])
        
        main_artist = artists[0] if artists else ""
        query = f"{song_title} {main_artist} {song['anime']}"
        
        raw_yt_url, raw_sp_url = None, None 
        yt_url, sp_url = None, None       
        
        anisongs_search_tasks = []
        
        if provider in ("youtube", "both"):
            anisongs_search_tasks.append(search_youtube(query))
        if provider in ("spotify", "both"):
            anisongs_search_tasks.append(search_spotify(song_title, main_artist))
            
        if anisongs_search_tasks:
            response = await asyncio.gather(*anisongs_search_tasks, return_exceptions=True)
            
            if provider == "spotify":
                raw_sp_url = response[0]
            elif provider == "youtube":
                raw_yt_url = response[0]
            elif provider == "both":
                raw_yt_url, raw_sp_url = response

            if isinstance(raw_yt_url, BaseException):
                yt_url = None
            else:
                yt_url = raw_yt_url

            if isinstance(raw_sp_url, BaseException):
                sp_url = None
            else:
                sp_url = raw_sp_url
            
        anisongs_only.append({
            "anime": song["anime"],
            "song_title": song["song_title"],
            "theme_type": song["theme_type"],
            "youtube_url": yt_url,
            "spotify_url": sp_url
        })

    return {"count": len(anisongs_only), "results": anisongs_only}

@router.get("/criteria")
async def search_anisong_by_criteria(
    year: Optional[int] = Query(None, description="Filter by year (2025|2024|2023|2022|...)"),
    season: Optional[str] = Query(None, regex="^(Winter|Spring|Summer|Fall)"),
    genre: Optional[str] = Query(None, description="Filter by genre (Action|Romance|Comedy|Drama|...)"),
    limit: int = Query(25, ge=1, le=50)
):
    
    anisongs = await fetch_anisong_criteria(
        year=year,
        season=season,
        genre=genre,
        limit=limit
    )
    
    if not anisongs:
        return {"count": 0, "results": []}
    
    anisongs_results = []
    for song in anisongs:
        title = song.get("song_title", "")
        artists = song.get("artists", [])
        
        main_artist = artists[0] if artists else ""
        query = f"{title} {main_artist} {song.get('anime', '')}"
        
        yt_task = search_youtube(query)
        sp_task = search_spotify(title, main_artist)
        raw_yt_url, raw_sp_url = await asyncio.gather(yt_task, sp_task, return_exceptions=True)

        if isinstance(raw_yt_url, BaseException):
            yt_url = None
        else:
            yt_url = raw_yt_url
        
        if isinstance(raw_sp_url, BaseException):
            sp_url = None
        else:
            sp_url = raw_sp_url
            
        anisongs_results.append({
            "anime": song["anime"],
            "song_title": song["song_title"],
            "theme_type": song["theme_type"],
            "youtube_url": yt_url,
            "spotify_url": sp_url
        })    
        
    return {"count": len(anisongs_results), "results": anisongs_results}