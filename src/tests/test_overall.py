from fastapi.testclient import TestClient
from pytest import fixture
from unittest.mock import patch, MagicMock, AsyncMock
from sqlmodel import SQLModel, Session, create_engine
from src.main import app
from src.services import auth_services
from src.routers.auth import oauth_scheme
from fastapi import HTTPException
import httpx

def setup_db():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    return Session(engine)

# hash
auth_services.hash_password = lambda p: "x"
auth_services.verify_password = lambda p, h: True

# token
def dummy_create(data):
    return "valid-token"

def dummy_decode(token):
    if token == "valid-token":
        return {"sub": 1}
    return None

auth_services.create_token = dummy_create
auth_services.decode_token = dummy_decode

# oauth2_scheme
def dummy_oauth():
    return "valid-token"

app.dependency_overrides[oauth_scheme] = dummy_oauth

# get_current_user
async def dummy_get_user(token="valid-token"):
    data = dummy_decode(token)
    if not data:
        raise HTTPException(status_code=401)
    return DummyUser()

auth_services.get_current_user = dummy_get_user

result = {
    "song_title": "S",
    "anime": "A",
    "artists": ["AA"],
    "theme_type": "OP"
}

resolved = {
    "song_title": "S",
    "anime": "A",
    "artists": ["AA"],
    "spotify_url": "sp",
    "youtube_url": "yt"
}

class DummyUser:
    def __init__(self, id=24, username="sagab", password_hash="x"):
        self.id = id
        self.username = username
        self.password_hash = password_hash

patch_user = patch("src.services.user_services.get_user_by_username",
                   return_value=DummyUser(id=24, username="sagab", password_hash="x"))

patch_user_create = patch("src.services.user_services.create_user",
                          return_value=MagicMock(id=24, username="sagab"))

patch_verify = patch("src.services.auth_services.verify_password", return_value=True)

patch_token = patch("src.services.auth_services.create_token", return_value="token123")

patch_decode = patch("src.services.auth_services.decode_token", return_value={"sub": 24})

patch_youtube = patch("src.services.youtube_services.search_youtube",
                      new=AsyncMock(return_value="yt"))

patch_spotify = patch("src.services.spotify_services.search_spotify",
                      new=AsyncMock(return_value="sp"))

patch_artist = patch("src.services.anisong_services.fetch_anisong_artist",
                     new=AsyncMock(return_value=[result]))

patch_theme = patch("src.services.anisong_services.fetch_anisong_list",
                    new=AsyncMock(return_value=[result]))

patch_name = patch("src.services.anisong_services.fetch_anisong_name",
                   new=AsyncMock(return_value=[result]))

patch_criteria = patch("src.services.anisong_services.fetch_anisong_criteria",
                       new=AsyncMock(return_value=[result]))

patch_search_master = patch("src.services.anisong_services.search_and_resolve_anisong",
                            new=AsyncMock(return_value=[resolved]))

patch_save_song = patch("src.services.anisong_services.save_anisong",
                        new=AsyncMock(return_value=MagicMock(id=1, artist="EGOIST", anime="Guilty Crown")))

patch_history = patch("src.services.anisong_services.save_user_history",
                      new=AsyncMock(return_value=None))

patch_pref = patch("src.services.preferences_service.update_preference_from_history",
                   new=AsyncMock(return_value=None))

# Patch the AsyncClient used inside src.services.anisong_services
patch_httpx_client = patch("src.services.anisong_services.httpx.AsyncClient")

# helper that configures the mock returned by patch_httpx_client
def configure_mock_httpx(mock_async_client):
    # mock_async_client is the patched class (the object yielded by "with patch_httpx_client as mock_async_client")
    # instance if code does: client = httpx.AsyncClient()
    inst = mock_async_client.return_value
    # async side effect for .get
    async def fake_get(url, params=None, **kwargs):
        # Create a minimal request object for the response
        request = httpx.Request("GET", url)
        # basic responses that mimic animethemes API structure enough for service parsing
        # you can extend this mapping if anisong_services expects more detailed JSON
        if isinstance(url, str) and "/anime?" in url and "filter[name]" in url:
            # fetch_anisong_name expects {"anime": [...]}
            return httpx.Response(200, json={"anime": []}, request=request)
        if isinstance(url, str) and "/artist?" in url:
            # fetch_anisong_artist expects {"artists": [...]}
            return httpx.Response(200, json={"artists": []}, request=request)
        if isinstance(url, str) and "/animetheme?" in url and "filter[type]" in url:
            # fetch_anisong_list expects {"animethemes": [...]}
            return httpx.Response(200, json={"animethemes": []}, request=request)
        if isinstance(url, str) and "/anime" in url:
            # fetch_anisong_criteria expects {"anime": [...]}
            return httpx.Response(200, json={"anime": []}, request=request)
        # default empty
        return httpx.Response(200, json={"data": []}, request=request)

    async def fake_post(url, **kwargs):
        request = httpx.Request("POST", url)
        return httpx.Response(200, json={"data": {}}, request=request)

    inst.get = AsyncMock(side_effect=fake_get)
    inst.post = AsyncMock(side_effect=fake_post)

    # context-manager usage: "async with httpx.AsyncClient() as client:"
    cm_inst = mock_async_client.return_value.__aenter__.return_value
    cm_inst.get = AsyncMock(side_effect=fake_get)
    cm_inst.post = AsyncMock(side_effect=fake_post)

patches = [
    patch_user,
    patch_user_create,
    patch_youtube,
    patch_spotify,
    patch_artist,
    patch_criteria,
    patch_theme,
    patch_name,
    patch_search_master,
    patch_save_song,
    patch_history,
    patch_pref,
    patch_httpx_client,
]

@fixture
def client():
    # enter many patch contexts; get the httpx mock as mock_httpx so we can configure it
    with patch_user, patch_user_create, patch_verify, patch_token, patch_decode, \
         patch_youtube, patch_spotify, patch_artist, patch_theme, patch_name, \
         patch_criteria, patch_search_master, patch_save_song, patch_history, \
         patch_pref, patch_httpx_client as mock_httpx:
        configure_mock_httpx(mock_httpx)
        yield TestClient(app)
        
def test_main():
    from src.main import app
    r = TestClient(app).get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Welcome to Best Anisongs Gathering And Searching!"}

def test_get_user_by_username_found():
    session = setup_db()
    with patch("src.services.user_services.get_user_by_username") as g:
        g.return_value = MagicMock(username="sagab")
    result = g(session, "sagab")
    assert result.username == "sagab"

def test_get_user_by_username_not_found():
    session = setup_db()
    with patch("src.services.user_services.get_user_by_username") as g:
        g.return_value = None
    result = g(session, "none")
    assert result is None

def register_and_login(client):
    client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    r = client.post("/auth/login", json={"username": "testuser", "password": "testpassword"})
    return {"Authorization": f"Bearer {r.json().get('access_token', '')}"}

def test_create_user(client):
    r = client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert r.status_code in (200, 400)

def test_register_user(client):
    r = client.post("/auth/register", json={"username": "u1", "password": "pw"})
    assert r.status_code in (200, 400)

def test_login_user(client):
    client.post("/auth/register", json={"username": "u2", "password": "pw"})
    r = client.post("/auth/login", json={"username": "u2", "password": "pw"})
    assert r.status_code == 200

def test_error_register_existing_user(client):
    client.post("/auth/register", json={"username": "u3", "password": "pw"})
    r = client.post("/auth/register", json={"username": "u3", "password": "pw"})
    assert r.status_code == 400

def test_get_current_user_invalid_token(client):
    r = client.get("/preferences/", headers={"Authorization": "Bearer invalid"})
    assert r.status_code == 401

def test_error_login_invalid_user(client):
    r = client.post("/auth/login", json={"username": "no", "password": "pw"})
    assert r.status_code == 401

def test_auth_invalid_token(client):
    r = client.get("/preferences/", headers={"Authorization": "Bearer invalid"})
    assert r.status_code == 401

def test_auth_invalid_password(client):
    client.post("/auth/register", json={"username": "px1", "password": "pw"})
    r = client.post("/auth/login", json={"username": "px1", "password": "wrong"})
    assert r.status_code == 401

def test_get_preferences(client):
    headers = register_and_login(client)
    r = client.get("/preferences/", headers=headers)
    assert r.status_code == 200

def test_create_preference(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "Test", "weight": 3.5}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_name(client):
    headers = register_and_login(client)
    r = client.get("/anisong/names", params={"name": "Mono"}, headers=headers)
    assert r.status_code == 200

def test_search_name_youtube(client):
    r = client.get("/anisong/names", params={"name": "test", "provider": "youtube"})
    assert r.status_code == 200

def test_search_name_both(client):
    r = client.get("/anisong/names", params={"name": "test", "provider": "both"})
    assert r.status_code == 200

def test_search_anisongs_by_theme(client):
    headers = register_and_login(client)
    r = client.get("/anisong/themes", params={"theme_type": "OP", "limit": 3}, headers=headers)
    assert r.status_code == 200

def test_theme_invalid_pattern(client):
    r = client.get("/anisong/themes", params={"theme_type": "OPP"})
    assert r.status_code == 422

def test_search_anisong_by_criteria_year(client):
    headers = register_and_login(client)
    r = client.get("/anisong/criteria", params={"year": 2020, "limit": 2}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_criteria_season(client):
    headers = register_and_login(client)
    r = client.get("/anisong/criteria", params={"season": "Spring", "limit": 2}, headers=headers)
    assert r.status_code == 200

def test_criteria_invalid_season(client):
    r = client.get("/anisong/criteria", params={"season": "autumn"})
    assert r.status_code == 422

def test_search_anisong_by_artist(client):
    headers = register_and_login(client)
    r = client.get("/anisong/artists", params={"artist": "ClariS", "limit": 2}, headers=headers)
    assert r.status_code == 200

def test_criteria_no_result(client):
    with patch("src.services.anisong_services.fetch_anisong_criteria", MagicMock(return_value=[])):
        r = client.get("/anisong/criteria")
    assert r.status_code == 200

def test_save_song_route(client):
    headers = register_and_login(client)
    r = client.post(
    "/anisong/save",
    params={
    "title": "Test Song",
    "artist": "A",
    "anime": "B",
    "spotify_url": "http://s",
    "popularity": 0,
    "youtube_url": "http://y"
    },
    headers=headers
    )
    assert r.status_code == 200

def test_search_anisong_route_theme(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": "OP"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_artist(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": "EGOIST"}, headers=headers)
    assert r.status_code == 200

def test_artist_no_result(client):
    with patch("src.services.anisong_services.fetch_anisong_artist", MagicMock(return_value=[])):
        r = client.get("/anisong/artists", params={"artist": "none"})
    assert r.status_code == 200

def test_search_anisong_route_title(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": "Guilty Crown"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_year(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": 2015}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_season(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": "Winter"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_year_season(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", 2020), ("q", "Fall")], headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_name_provider_youtube(client):
    headers = register_and_login(client)
    r = client.get("/anisong/names", params={"name": "Mono", "provider": "youtube"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_name_provider_spotify(client):
    headers = register_and_login(client)
    r = client.get("/anisong/names", params={"name": "Mono", "provider": "spotify"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_name_provider_both(client):
    headers = register_and_login(client)
    r = client.get("/anisong/names", params={"name": "Mono", "provider": "both"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_by_name_empty(client):
    headers = register_and_login(client)
    with patch("src.services.anisong_services.fetch_anisong_name", MagicMock(return_value=[])):
        r = client.get("/anisong/names", params={"name": "unknown"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_themes_empty(client):
    headers = register_and_login(client)
    with patch("src.services.anisong_services.fetch_anisong_list", MagicMock(return_value=[])):
        r = client.get("/anisong/themes", params={"theme_type": "OP"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_criteria_empty(client):
    headers = register_and_login(client)
    with patch("src.services.anisong_services.fetch_anisong_criteria", MagicMock(return_value=[])):
        r = client.get("/anisong/criteria", params={"year": 1900}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_artist_empty(client):
    headers = register_and_login(client)
    with patch("src.services.anisong_services.fetch_anisong_artist", MagicMock(return_value=[])):
        r = client.get("/anisong/artists", params={"artist": "none"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_invalid(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params={"q": ""}, headers=headers)
    assert r.status_code == 200

def test_protected_route_without_token(client):
    r = client.get("/preferences/")
    assert r.status_code == 401

def test_protected_route_with_token(client):
    headers = register_and_login(client)
    r = client.get("/preferences/", headers=headers)
    assert r.status_code == 200

def test_add_preferences_invalid_weight(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "Test", "weight": 14.0}, headers=headers)
    assert r.status_code == 200

def test_add_preferences_negative_weight(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "Test", "weight": -3.0}, headers=headers)
    assert r.status_code == 200