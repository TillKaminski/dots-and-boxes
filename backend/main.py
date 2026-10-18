"""Python Main-File (APIs)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.game.game_service import GameService
from backend.game.api.router import router as game_router

app = FastAPI()
service = GameService()

app.include_router(game_router)


# CORS-Filter Domains:
origins = [
    "http://localhost:4200",
    "http://localhost:4201",
    "http://localhost:4202",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Enable Cookies
    allow_methods=["*"],  # Enable Methods (GET, POST, PUT, DELETE, ...)
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Returns message for Standard Link.

    Returns:
        Root message.
    """
    return {
        "root-message": "Fast-API Entrypoint.",
        "api-version": "v1",
        "status": "running",
    }
