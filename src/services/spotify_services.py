from dotenv import load_dotenv
import os
import httpx

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

async def get_spotify_token():
    async with httpx.AsyncClient() as client:
        auth = (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        data = {"grant_type": "client_credentials"}
        response = await client.post(TOKEN_URL, auth=auth, data=data)
        response.raise_for_status()
        return response.json().get("access_token")
    
async def search_spotify(query: str):
    token = await get_spotify_token()
    headers = {"Authorization" : f"Bearer {token}"}
    params = { "q" : query, "type" : "track", "limit" : 1}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("tracks", {}).get("items", [])
        
        if items:
            return items[0].get("external_urls").get("spotify")
        return None
    