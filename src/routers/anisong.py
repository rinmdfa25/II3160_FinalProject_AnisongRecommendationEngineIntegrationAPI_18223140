from fastapi import APIRouter, Query
from src.services.anisong_services import fetch_anisong_list
from src.services.youtube_service import search_youtube
from src.services.spotify_services import search_spotify
import asyncio

router = APIRouter(
    prefix="/anisong",
    tags=["anisong"]
)

@router.get("/themes")
async def search_anisongs_by_theme(theme_type: str = Query(..., regex="^(OP|ED|INS)$"), limit: int = 5):
    anisongs = await fetch_anisong_list(theme_type, limit)
    anisongs_results = []
    
    for song in anisongs:
        query =  f"{song['song_title']} {song['anime']} {song['theme_type']}"
         
        yt_url, sp_url = await asyncio.gather(search_youtube(query), search_spotify(query), return_exceptions=True)
        
        if isinstance(yt_url, Exception):
            yt_url = None
        if isinstance(sp_url, Exception):
            sp_url = None
            
        anisongs_results.append({
            "anime": song["anime"],
            "theme_type": song["theme_type"],
            "song_title": song["song_title"],
            "youtube_url": yt_url,
            "spotify_url": sp_url
        })
    
    return {"count": len(anisongs_results), "results": anisongs_results}

@router.get("/names")
async def search_anisong_by_name(
    name: str = Query(..., description="Name of anisong or anime title"),
    provider: str = Query("spotify", regex="^(spotify|youtube|both)$")
):
    theme_type = ["OP", "ED", "INS"]
    anisongs = await fetch_anisong_list(theme_type=theme_type, limit=5)    
    anisongs_only_filtered = [s for s in anisongs if name.lower() in s["anime"].lower()  or name.lower() in s["song_title"].lower()]

    if not anisongs_only_filtered:
        return {"count": 0, "results": []}
    
    anisongs_only = []
    for song in anisongs_only_filtered:
        query = f"{song['song_title']} {song['anime']} {song['theme_type']}"
        yt_url, sp_url = None, None
        anisongs_search_tasks = []
        
        if provider in ("youtube", "both"):
            anisongs_search_tasks.append(search_youtube(query))
        if provider in ("spotify", "both"):
            anisongs_search_tasks.append(search_spotify(query))
            
        if anisongs_search_tasks:
            response = await asyncio.gather(*anisongs_search_tasks, return_exceptions=True)
            if provider == "spotify":
                sp_url = response[0]
            elif provider == "youtube":
                yt_url = response[0]
            elif provider == "both":
                sp_url, yt_url = response
        
        anisongs_only.append({
            "anime": song["anime"],
            "song_title": song["song_title"],
            "theme_type": song["theme_type"],
            "youtube_url": yt_url,
            "spotify_url": sp_url
        })

    return {"count": len(anisongs_only), "results": anisongs_only}
    
