"""
config.py — Configuration centralisée de l'application

Utilise Pydantic Settings pour charger et valider les variables d'environnement.
Toutes les configurations sont centralisées ici pour faciliter la maintenance.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import os
import sys


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    """Configuration de l'application chargée depuis .env"""
    
    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "postgresql://postgres:password@localhost:5432/cryptotracker"
    
    # ── JWT Authentication ────────────────────────────────────────────────
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 heures
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Valide que la SECRET_KEY est sécurisée
        
        Vérifie que :
        - La clé n'est pas la valeur par défaut
        - La clé fait au moins 32 caractères
        - En production, la clé DOIT être définie via variable d'environnement
        
        Raises:
            ValueError: Si la clé n'est pas sécurisée
        """
        environment = os.getenv("ENVIRONMENT", "development")
        
        # Vérifier si c'est la clé par défaut
        if v == "your-secret-key-change-in-production":
            print("\n" + "="*70)
            print("🚨 ERREUR DE SÉCURITÉ : SECRET_KEY par défaut détectée!")
            print("="*70)
            print("\nLa SECRET_KEY doit être changée en production.")
            print("\nPour générer une clé sécurisée, exécutez :")
            print("  openssl rand -hex 32")
            print("\nOu en Python :")
            print("  python -c 'import secrets; print(secrets.token_hex(32))'")
            print("\nPuis définissez la variable d'environnement SECRET_KEY")
            print("ou mettez à jour backend/.env avec la nouvelle clé.")
            print("="*70 + "\n")
            
            # En production, BLOQUER l'application
            if environment == "production":
                raise ValueError(
                    "SECRET_KEY par défaut interdite en production. "
                    "Définissez SECRET_KEY via variable d'environnement."
                )
            else:
                print("⚠️  Mode développement : Clé par défaut acceptée (NON SÉCURISÉ)\n")
        
        # Vérifier la longueur minimale
        if len(v) < 32:
            raise ValueError(
                f"SECRET_KEY doit faire au moins 32 caractères (actuellement: {len(v)}). "
                "Générez une clé sécurisée avec: openssl rand -hex 32"
            )
        
        # En production, vérifier que la clé vient bien d'une variable d'environnement
        if environment == "production" and not os.getenv("SECRET_KEY"):
            raise ValueError(
                "En production, SECRET_KEY DOIT être définie via variable d'environnement. "
                "Ne jamais hardcoder les secrets dans le code."
            )
        
        return v
    
    # ── CoinGecko API ─────────────────────────────────────────────────────
    coingecko_url: str = "https://api.coingecko.com/api/v3"
    api_timeout: float = 10.0
    detail_timeout: float = 15.0
    
    # ── Redis Cache ───────────────────────────────────────────────────────
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_socket_timeout: float = 5.0
    redis_socket_connect_timeout: float = 5.0
    redis_decode_responses: bool = True
    
    # ── Cache TTL (Time To Live) ──────────────────────────────────────────
    # TTL augmentés pour réduire drastiquement les appels à CoinGecko
    prices_ttl: int = 120     # 2 minutes (au lieu de 30s)
    search_ttl: int = 600     # 10 minutes (au lieu de 5min)
    history_ttl: int = 600    # 10 minutes (au lieu de 5min)
    detail_ttl: int = 300     # 5 minutes (au lieu de 2min)
    
    # ── CORS ──────────────────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:5173"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convertit la chaîne ALLOWED_ORIGINS en liste"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # ── Logging ───────────────────────────────────────────────────────────
    log_level: str = "INFO"
    


# Instance globale des settings
settings = Settings()

 
