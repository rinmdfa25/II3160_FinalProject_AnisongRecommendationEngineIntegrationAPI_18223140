import httpx

BASE_URL = "https://api.animethemes.moe"

async def fetch_anisong_list(theme_type: str = "OP", limit: int = 5):
    url = f"{BASE_URL}/anime?sort=-year&limit={limit}&include=animethemes.animethemeentries.videos"
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
        res.raise_for_status()
        data = res.json()

    anime_context_only = []
    for anime in data.get("anime", []):
        anime_name = anime.get("name")
        for theme in anime.get("animethemes", []):
            if theme.get("type") and theme["type"].upper() == theme_type.upper():
                anime_context_only.append({
                    "anime": anime_name,
                    "song_title": theme.get("slug"),
                    "theme_type": theme["type"]
                })
    return anime_context_only

