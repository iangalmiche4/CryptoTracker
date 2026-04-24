"""
main.py — API backend CryptoTracker

Point d'entrée de l'application FastAPI.
Configuration minimale : CORS, logging, enregistrement des routers.

Architecture RESTful :
- config.py : Configuration centralisée
- core/ : Modules de base (cache Redis, exceptions, security)
- services/ : Logique métier (coingecko_service)
- routers/ : Endpoints REST (sessions, users, coins, alerts, portfolio)
- models.py : Modèles SQLAlchemy
- schemas.py : Schémas Pydantic avec HATEOAS
- middleware/ : Middlewares personnalisés (exceptions, logging)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from config import settings
from routers import auth, user, coingecko, holdings
from middleware import exception_handler_middleware, request_logging_middleware

# ── Configuration du logging ──────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("cryptotracker")

# ── Rate Limiting ─────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)

# Custom rate limit exception handler
async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle rate limit exceeded exceptions"""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

# ── Application ───────────────────────────────────────────────────────

app = FastAPI(
    title="CryptoTracker API",
    version="3.0.0",
    description="API backend pour CryptoTracker avec Redis cache et architecture en couches",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Attacher le limiter à l'application
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    allow_credentials=True,
)

# ── Custom Middlewares ────────────────────────────────────────────────

# 1. Request Logging (premier pour logger toutes les requêtes)
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log toutes les requêtes avec métriques de performance"""
    return await request_logging_middleware(request, call_next)

# 2. Exception Handler (gestion globale des erreurs)
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    """Gestion centralisée des exceptions"""
    return await exception_handler_middleware(request, call_next)

# 3. Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # CSP plus permissive pour Swagger UI/ReDoc
    # Permet les ressources inline et les CDN nécessaires pour la documentation
    if request.url.path.startswith("/api/docs") or request.url.path.startswith("/api/redoc") or request.url.path.startswith("/api/openapi.json"):
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' data: https://cdn.jsdelivr.net;"
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
    
    return response

# ── Enregistrement des routers ────────────────────────────────────────

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(coingecko.router)
app.include_router(holdings.router)

# ── Endpoint racine avec HATEOAS ──────────────────────────────────────

@app.get("/")
def root():
    """Point de contrôle : vérifie que le serveur tourne"""
    logger.info("Health check endpoint called")
    return {
        "message": "CryptoTracker API is running",
        "version": "3.0.0",
        "architecture": "Layered architecture with Redis cache",
        "docs": "/api/docs"
    }

 