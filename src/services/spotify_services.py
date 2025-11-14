from dotenv import load_dotenv
import os
from fastapi import params
import httpx
import time

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

_cached_token = None
_token_exp = 0

async def get_spotify_token():
    global _cached_token, _token_exp
    now = time.time()
    
    if _cached_token and now < _token_exp:
        return _cached_token
    
    async with httpx.AsyncClient() as client:
        auth = (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        data = {"grant_type": "client_credentials"}
        response = await client.post(TOKEN_URL, auth=auth, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        
        _cached_token = token_data["access_token"]
        _token_exp = now + token_data["expires_in"] - 60
        
        return _cached_token
    
async def search_spotify(title, artist, anime=None):
    token = await get_spotify_token()
    headers = {"Authorization" : f"Bearer {token}"}
    base_params = {"type": "track", "limit": 5, "market": "JP"}
    query = []
    
    if artist: 
        query.append(f"track:{title} artist:{artist}")

    query.append(f"track:{title}")
    
    if anime:
        query.append(f"{title} {anime}")
    
    async with httpx.AsyncClient() as client:
        for q in query:
            params = base_params | {"q": q}
        
            response = await client.get(SEARCH_URL, headers=headers, params=params)
            if response.status_code != 200:
                continue
            
            data = response.json()
            items = data.get("tracks", {}).get("items", [])
            
            if not items:
                return None
        return items[0]["external_urls"]["spotify"]
    