"""
config.py — Configuration centralisée de l'application

Utilise Pydantic Settings pour charger et valider les variables d'environnement.
Toutes les configurations sont centralisées ici pour faciliter la maintenance.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuration de l'application chargée depuis .env"""
    
    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "postgresql://postgres:password@localhost:5432/cryptotracker"
    
    # ── JWT Authentication ────────────────────────────────────────────────
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 heures
    
    # ── CoinGecko API ─────────────────────────────────────────────────────
    coingecko_url: str = "https://api.coingecko.com/api/v3"
    api_timeout: float = 10.0
    detail_timeout: float = 15.0
    
    # ── Cache TTL (Time To Live) ──────────────────────────────────────────
    prices_ttl: int = 30      # 30 secondes
    search_ttl: int = 300     # 5 minutes
    history_ttl: int = 300    # 5 minutes
    detail_ttl: int = 120     # 2 minutes
    
    # ── CORS ──────────────────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:5173"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convertit la chaîne ALLOWED_ORIGINS en liste"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # ── Logging ───────────────────────────────────────────────────────────
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instance globale des settings
settings = Settings()

 
