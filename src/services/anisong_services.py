import httpx

BASE_URL = "https://api.animethemes.moe"

async def fetch_anisong_list(theme_type: str = "OP", limit: int = 5):
    url = (
        f"{BASE_URL}/animetheme?"
        f"filter[type]={theme_type}"
        f"&sort=-anime.year"
        f"&limit={limit}"
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

