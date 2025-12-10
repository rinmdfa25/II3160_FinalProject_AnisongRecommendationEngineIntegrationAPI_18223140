from dotenv import load_dotenv
import os
import httpx


load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

BASE_URL = "https://www.googleapis.com/youtube/v3/search"

async def search_youtube(query: str):
    params = {
        "part": "snippet",
        "q": query,
        "maxResults": 1,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data["items"]:
                video_id = data["items"][0]["id"]["videoId"]
                return f"https://www.youtube.com/watch?v={video_id}"
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                return None
            raise e
    