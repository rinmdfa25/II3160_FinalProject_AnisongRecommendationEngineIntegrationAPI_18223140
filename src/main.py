from fastapi import FastAPI
from src.routers import anisong

app = FastAPI(
    title="Best Anisongs Gathering And Searching",
    version="1.0.0"
)

app.include_router(anisong.router)

@app.get("/")
def main():
    return {"message": "Welcome to Best Anisongs Gathering And Searching!"}

