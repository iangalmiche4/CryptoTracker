"""
main.py — API backend CryptoTracker

Point d'entrée de l'application FastAPI.
Configuration minimale : CORS, logging, enregistrement des routers.

Architecture :
- config.py : Configuration centralisée
- core/ : Modules de base (cache, exceptions, security)
- services/ : Logique métier (coingecko_service)
- routers/ : Endpoints REST (auth, user, coingecko)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings
from routers import auth, user, coingecko

# ── Configuration du logging ──────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cryptotracker")

# ── Application ───────────────────────────────────────────────────────

app = FastAPI(
    title="CryptoTracker API",
    version="2.0.0",
    description="API backend pour CryptoTracker avec architecture améliorée"
)

# ── CORS ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ── Enregistrement des routers ───────────────────────────────────────

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(coingecko.router)

# ── Endpoint racine ───────────────────────────────────────────────────

@app.get("/")
def root():
    """Point de contrôle : vérifie que le serveur tourne"""
    logger.info("Health check endpoint called")
    return {
        "message": "CryptoTracker API is running",
        "version": "2.0.0",
        "architecture": "Refactored with service layer pattern"
    }

 