"""
schemas.py — Schémas Pydantic pour la validation des requêtes/réponses

Responsabilités :
  - Valider les données entrantes (requêtes)
  - Formater les données sortantes (réponses)
  - Documenter l'API automatiquement (Swagger)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ── Schémas d'authentification ───────────────────────────────────────

class UserRegister(BaseModel):
    """Schéma pour l'inscription d'un nouvel utilisateur"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe (min 8 caractères)")

class Token(BaseModel):
    """Schéma de réponse après authentification réussie"""
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Type de token")


class UserResponse(BaseModel):
    """Schéma de réponse pour les informations utilisateur"""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Permet la conversion depuis un modèle SQLAlchemy


# ── Schémas pour les coins suivis ─────────────────────────────────────

class CoinCreate(BaseModel):
    """Schéma pour ajouter un coin à suivre"""
    coin_id: str = Field(..., description="ID CoinGecko (ex: bitcoin)")
    position: Optional[int] = Field(None, description="Position dans la liste (optionnel)")


class CoinResponse(BaseModel):
    """Schéma de réponse pour un coin suivi"""
    id: int
    coin_id: str
    position: int
    created_at: datetime

    class Config:
        from_attributes = True


class CoinsReorder(BaseModel):
    """Schéma pour réorganiser plusieurs coins (drag & drop)"""
    coin_ids: list[str] = Field(..., description="Liste ordonnée des coin_ids")


# ── Schémas pour les alertes ──────────────────────────────────────────

class AlertCreate(BaseModel):
    """Schéma pour créer une alerte de prix"""
    coin_id: str = Field(..., description="ID CoinGecko (ex: bitcoin)")
    type: str = Field(..., description="Type d'alerte : 'high' ou 'low'")
    threshold: float = Field(..., gt=0, description="Seuil de prix en USD")


class AlertUpdate(BaseModel):
    """Schéma pour mettre à jour une alerte"""
    threshold: float = Field(..., gt=0, description="Nouveau seuil de prix en USD")


class AlertResponse(BaseModel):
    """Schéma de réponse pour une alerte"""
    id: int
    coin_id: str
    type: str
    threshold: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Schémas pour les réponses groupées ────────────────────────────────

class UserDataResponse(BaseModel):
    """Schéma de réponse pour toutes les données utilisateur"""
    user: UserResponse
    coins: list[CoinResponse]
    alerts: list[AlertResponse]

 
