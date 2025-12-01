# II3160_FinalProject_AnisongRecommendationEngineIntegrationAPI_18223140

![finally](docs/mono-weekend-animation-ann-kiriyama-sleeping-after-doing-many-tasks.gif)

This Project is dedicated to fulfill one of the index of one of the subject (II3160 - Integrated System Technology). This project contain of anisong searching based on the song artists, source of the animes, year or season were this song released. Follow up by User Preferences based on anisongs searching.

# Name of The Project

Best
Anisongs
Gathering
And
Searching

# Requirements

- Python: 3.12 or more
- Spotify Client ID and Client Secret
  For Getting Spotify Client ID and Client Secret, follow the steps from link below

```
https://developer.spotify.com/documentation/web-api/tutorials/getting-started
```

- Youtube Data API Key
  For Getting Youtube Data API Key, follow the steps from link below

```
https://console.cloud.google.com/marketplace/product/google/youtube.googleapis.com?project=youtubedataapi-477815
```

- JWT Key
  For Getting JWT Key, follow the steps from link below

```
https://jwtsecrets.com/
```

# Environment Variables

Make One .env file and fill this below

```
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
SPOTIFY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET
JWT_SECRET=YOUR_JWT_SECRET
```

# Installation for Local Use

- Clone this repository to your local storage

```
git clone https://github.com/rinmdfa25/II3160_FinalProject_AnisongRecommendationEngineIntegrationAPI_18223140.git
```

- Set up The Environment

```
python -m venv env
```

- Activate the Environment

```
.venv\Scripts\activate.ps1
```

- Install uv

```
pip install uv
```

- Install all the dependencies

```
uv pip install -r requirement.txt
```

- Insert The API Key from Youtube, Spotify, and JWT to your Configuration Environment (.env)

```
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
SPOTIFY_CLIENT_ID=YOUR_SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_SPOTIFY_CLIENT_SECRET
JWT_SECRET=YOUR_JWT_SECRET
```

- Run the Application

```
uv uvicorn src.main:app --reload
```

- Open your local browser or Run it with Postman
  Usually using localhost address

```
http://127.0.0.1/8000
```

# Set up The Docker Container

- Make sure the Dockerfile, compose.yaml, and requirement.txt are included in folder

- Build the Docker

```
docker compose build
```

- Run the docker build

```
docker compose up -d
```

# Open Up The Browser and use The endpoints

- Open up http://localhost:8000/docs#/ to see and use the endpoints.

# Endpoints to use

- Authentication

```
POST /auth/login {username: string, password: string}
POST /auth/register {username: string, password: string}
```

- Anisongs Searching

```
GET /anisong/themes
GET /anisong/names
GET /anisong/artists
GET /anisong/criteria
POST /anisong/search {q: list of string}
```

- User Preferences

```
GET /preferences/
POST /preferences/ {tag: string, weight: float}
```

# Credits

This API Integration with the purpose for education use and not affiliated with AnimeThemes, Youtube, and Spotify. It was all used with the integration with public API, credits to:

- AnimeThemes<br/>
  ![animethemes](https://avatars.githubusercontent.com/u/72712310?s=200&v=4)

```
https://api-docs.animethemes.moe/
```

- Youtube<br/>
  ![youtube](https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png)

```
https://developers.google.com/youtube/v3/docs
```

- Spotify<br/>
  ![spotify](https://upload.wikimedia.org/wikipedia/commons/7/74/Spotify_App_Logo.svg)

```
https://developer.spotify.com/documentation/web-api
```
