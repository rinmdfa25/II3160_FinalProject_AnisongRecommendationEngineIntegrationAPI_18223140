from fastapi import FastAPI
from src.routers import anisong, auth, preferences
from src.utils.sqlite import create_db_and_tables

app = FastAPI(
    title="Best Anisongs Gathering And Searching",
    version="1.0.0"
)

app.include_router(preferences.router)
app.include_router(anisong.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_start():
    create_db_and_tables()
    
@app.get("/")
def main():
    return {"message": "Welcome to Best Anisongs Gathering And Searching!"}