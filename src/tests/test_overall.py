from fastapi.testclient import TestClient
from pytest import fixture
from sqlmodel import Session, SQLModel, create_engine
from src.services.user_services import get_user_by_username, create_user
from src.services.anisong_services import search_youtube, search_spotify, fetch_anisong_artist, fetch_anisong_criteria

@fixture
def client():
	from src.main import app
	with TestClient(app) as c:
		yield c

def test_main():
    from src.main import app
    r = TestClient(app).get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Welcome to Best Anisongs Gathering And Searching!"}

def setup_db():
    engine = create_engine("sqlite://", echo=False)
    SQLModel.metadata.create_all(engine)
    return Session(engine)

def test_get_user_by_username_found():
    session = setup_db()
    create_user(session, "sagab", "sagab")
    result = get_user_by_username(session, "sagab")
    assert result is not None
    assert result.username == "sagab"

def test_get_user_by_username_not_found():
    session = setup_db()
    result = get_user_by_username(session, "nobody")
    assert result is None
    
def test_create_user(client):
    r = client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert r.status_code in (200, 400)
    
def register_and_login(client):
	client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
	r = client.post("/auth/login", json={"username": "testuser", "password": "testpassword"})
	token = r.json()["access_token"]
	return {"Authorization": f"Bearer {token}"}

def test_register_user(client):
    r = client.post("/auth/register", json={"username": "u1", "password": "pw"})
    assert r.status_code in (200, 400)

def test_login_user(client):
    client.post("/auth/register", json={"username": "u2", "password": "pw"})
    r = client.post("/auth/login", json={"username": "u2", "password": "pw"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_error_register_existing_user(client):
    client.post("/auth/register", json={"username": "u3", "password": "pw"})
    r = client.post("/auth/register", json={"username": "u3", "password": "pw"})
    assert r.status_code == 400
    
def test_get_current_user_invalid_token(client):
# token rusak supaya decode_token melempar error
    invalid_token = "this_is_not_jwt"

    response = client.get(
        "/preferences/",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired Token"
    
def test_error_login_invalid_user(client):
    r = client.post("/auth/login", json={"username": "nonexistent", "password": "pw"})
    assert r.status_code == 401

def test_auth_invalid_token(client):
    r = client.get("/preferences/", headers={"Authorization": "Bearer invalidtoken"})
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

def test_search_name_youtube(client, monkeypatch):
    monkeypatch.setattr(search_youtube, "__call__", lambda *a, **k: "yt")
    r = client.get("/anisong/names", params={"name":"test","provider":"youtube"})
    assert r.status_code == 200

def test_search_name_both(client, monkeypatch):
    monkeypatch.setattr(search_youtube, "__call__", lambda *a, **k: "yt")
    monkeypatch.setattr(search_spotify, "__call__", lambda *a, **k: "sp")
    r = client.get("/anisong/names", params={"name":"test","provider":"both"})
    assert r.status_code == 200

def test_search_anisongs_by_theme(client):
    headers = register_and_login(client)
    r = client.get("/anisong/themes", params={"theme_type": "OP", "limit": 3}, headers=headers)
    assert r.status_code == 200
    
def test_theme_invalid_pattern(client):
    r = client.get("/anisong/themes", params={"theme_type":"OPP"})
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
    r = client.get("/anisong/criteria", params={"season":"autumn"})
    assert r.status_code == 422


def test_search_anisong_by_artist(client):
    headers = register_and_login(client)
    r = client.get("/anisong/artists", params={"artist": "ClariS", "limit": 2}, headers=headers)
    assert r.status_code == 200

def test_criteria_no_result(client, monkeypatch):
    monkeypatch.setattr(fetch_anisong_criteria, "__call__", lambda **k: [])
    r = client.get("/anisong/criteria")
    assert r.json()["count"] == 80


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
    r = client.post("/anisong/search", params=[("q", "OP")], headers=headers)
    assert r.status_code == 200
    
def test_search_anisong_route_artist(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", "EGOIST")], headers=headers)
    assert r.status_code == 200

def test_artist_no_result(client, monkeypatch):
    monkeypatch.setattr(fetch_anisong_artist, "__call__", lambda *a, **k: [])
    r = client.get("/anisong/artists", params={"artist":"none"})
    assert r.status_code == 200
    assert r.json()["count"] == 0

def test_search_anisong_route_title(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", "Guilty Crown")], headers=headers)
    assert r.status_code == 200

def test_search_anisong_route_year(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", 2015)], headers=headers)
    assert r.status_code == 200
    
def test_search_anisong_route_season(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", "Winter")], headers=headers)
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
    r = client.get("/anisong/names", params={"name": "unknown_anime_name_xyz"}, headers=headers)
    data = r.json()
    assert r.status_code == 200
    assert data["count"] == 0

def test_search_anisong_themes_empty(client):
    headers = register_and_login(client)
    r = client.get("/anisong/themes", params={"theme_type": "OP", "limit": 1, "debug": "empty"}, headers=headers)
    assert r.status_code == 200

def test_search_anisong_criteria_empty(client):
    headers = register_and_login(client)
    r = client.get("/anisong/criteria", params={"year": 1900}, headers=headers)
    data = r.json()
    assert r.status_code == 200
    assert data["count"] == 0

def test_search_anisong_artist_empty(client):
    headers = register_and_login(client)
    r = client.get("/anisong/artists", params={"artist": "nonexistent_artist_xyz"}, headers=headers)
    data = r.json()
    assert r.status_code == 200
    assert data["count"] == 0
    
def test_search_anisong_route_invalid(client):
    headers = register_and_login(client)
    r = client.post("/anisong/search", params=[("q", "")], headers=headers)
    assert r.status_code == 200

def test_protected_route_without_token(client):
    r = client.get("/preferences/")
    assert r.status_code == 401
    
def test_protected_route_with_token(client):
    headers = register_and_login(client)
    r = client.get("/preferences/", headers=headers)
    assert r.status_code == 200

def test_add_preferences_empty(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "", "weight": 2.0}, headers=headers)
    assert r.status_code == 200
    
def test_add_preferences_invalid_weight(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "Test", "weight": 14.0}, headers=headers)
    assert r.status_code == 200
    
def test_add_preferences_negative_weight(client):
    headers = register_and_login(client)
    r = client.post("/preferences/", params={"tag": "Test", "weight": -3.0}, headers=headers)
    assert r.status_code == 200