"""
schemas.py — Schémas Pydantic pour la validation des requêtes/réponses

Responsabilités :
  - Valider les données entrantes (requêtes)
  - Formater les données sortantes (réponses)
  - Documenter l'API automatiquement (Swagger)
  - Implémenter HATEOAS (Hypermedia As The Engine Of Application State)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime


# ── HATEOAS : Liens Hypermedia ───────────────────────────────────────

class Link(BaseModel):
    """Lien hypermedia pour HATEOAS"""
    href: str = Field(..., description="URL de la ressource")
    method: str = Field(..., description="Méthode HTTP (GET, POST, PUT, DELETE)")
    rel: Optional[str] = Field(None, description="Relation avec la ressource actuelle")


class Links(BaseModel):
    """Collection de liens hypermedia"""
    self: Optional[Link] = None
    collection: Optional[Link] = None
    create: Optional[Link] = None
    update: Optional[Link] = None
    delete: Optional[Link] = None
    related: Optional[Dict[str, Link]] = None


# ── Schémas d'authentification ───────────────────────────────────────

class UserRegister(BaseModel):
    """Schéma pour l'inscription d'un nouvel utilisateur"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe (min 8 caractères)")


class SessionCreate(BaseModel):
    """Schéma pour créer une session (login)"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe")


class Token(BaseModel):
    """Schéma de réponse après authentification réussie"""
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")
    _links: Optional[Links] = None


class UserResponse(BaseModel):
    """Schéma de réponse pour les informations utilisateur"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    created_at: datetime
    _links: Optional[Links] = None


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour le profil utilisateur"""
    email: Optional[EmailStr] = Field(None, description="Nouvel email")
    password: Optional[str] = Field(None, min_length=8, description="Nouveau mot de passe")


# ── Schémas pour les coins (cryptomonnaies) ───────────────────────────

class CoinListResponse(BaseModel):
    """Schéma de réponse pour la liste des coins"""
    coins: List[Dict]
    total: int
    _links: Optional[Links] = None


class CoinDetailResponse(BaseModel):
    """Schéma de réponse pour les détails d'un coin"""
    id: str
    name: str
    symbol: str
    description: Optional[str] = None
    image: Optional[str] = None
    market_data: Optional[Dict] = None
    _links: Optional[Links] = None


class CoinPricesResponse(BaseModel):
    """Schéma de réponse pour les prix d'un coin"""
    coin_id: str
    prices: Dict
    _links: Optional[Links] = None


class CoinHistoryResponse(BaseModel):
    """Schéma de réponse pour l'historique d'un coin"""
    coin_id: str
    history: List[Dict]
    days: int
    _links: Optional[Links] = None


# ── Schémas pour la watchlist (coins suivis) ──────────────────────────

class WatchlistCreate(BaseModel):
    """Schéma pour ajouter un coin à la watchlist"""
    coin_id: str = Field(..., description="ID CoinGecko (ex: bitcoin)")


class WatchlistItemCreate(BaseModel):
    """Schéma pour ajouter un coin à la watchlist (avec position)"""
    coin_id: str = Field(..., description="ID CoinGecko (ex: bitcoin)")
    position: Optional[int] = Field(None, description="Position dans la liste (optionnel)")


class WatchlistItemResponse(BaseModel):
    """Schéma de réponse pour un coin de la watchlist"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    coin_id: str
    position: int
    created_at: datetime
    _links: Optional[Links] = None


class WatchlistReorderItem(BaseModel):
    """Item pour réorganiser la watchlist"""
    coin_id: str
    position: int


class WatchlistReorder(BaseModel):
    """Schéma pour réorganiser la watchlist (drag & drop)"""
    items: List[WatchlistReorderItem] = Field(..., description="Liste des coins avec nouvelles positions")


class WatchlistResponse(BaseModel):
    """Schéma de réponse pour la watchlist complète"""
    items: List[WatchlistItemResponse]
    total: int
    _links: Optional[Links] = None


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
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    coin_id: str
    type: str
    threshold: float
    created_at: datetime
    _links: Optional[Links] = None


class AlertsResponse(BaseModel):
    """Schéma de réponse pour la liste des alertes"""
    alerts: List[AlertResponse]
    total: int
    _links: Optional[Links] = None


# ── Schémas pour les holdings (portfolio) ─────────────────────────────

class HoldingCreate(BaseModel):
    """Schéma pour créer un holding"""
    coin_id: str = Field(..., description="ID CoinGecko (ex: bitcoin)")
    quantity: float = Field(..., gt=0, description="Quantité possédée")
    purchase_price: float = Field(..., gt=0, description="Prix d'achat en USD")
    purchase_date: datetime = Field(..., description="Date d'achat")
    notes: Optional[str] = Field(None, max_length=500, description="Notes optionnelles")


class HoldingUpdate(BaseModel):
    """Schéma pour mettre à jour un holding"""
    quantity: Optional[float] = Field(None, gt=0, description="Nouvelle quantité")
    purchase_price: Optional[float] = Field(None, gt=0, description="Nouveau prix d'achat")
    purchase_date: Optional[datetime] = Field(None, description="Nouvelle date d'achat")
    notes: Optional[str] = Field(None, max_length=500, description="Nouvelles notes")


class HoldingResponse(BaseModel):
    """Schéma de réponse pour un holding"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    coin_id: str
    quantity: float
    purchase_price: float
    purchase_date: datetime
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    _links: Optional[Links] = None


class HoldingWithStats(HoldingResponse):
    """Holding enrichi avec statistiques calculées"""
    current_price: float
    current_value: float
    total_gain_loss: float
    gain_loss_percentage: float


class HoldingsResponse(BaseModel):
    """Schéma de réponse pour la liste des holdings"""
    holdings: List[HoldingWithStats]
    total: int
    _links: Optional[Links] = None


class PortfolioSummary(BaseModel):
    """Schéma de réponse pour le résumé du portfolio"""
    total_invested: float
    current_value: float
    total_gain_loss: float
    gain_loss_percentage: float
    holdings_count: int
    _links: Optional[Links] = None


# ── Schémas pour le cache (monitoring) ────────────────────────────────

class CacheStatsResponse(BaseModel):
    """Schéma de réponse pour les statistiques du cache"""
    available: bool
    hits: int
    misses: int
    errors: int
    hit_rate: str
    total_requests: int
    redis_version: Optional[str] = None
    used_memory_human: Optional[str] = None
    keys_count: Optional[int] = None
    _links: Optional[Links] = None


# ── Fonctions utilitaires pour HATEOAS ────────────────────────────────

def create_links(base_url: str, resource_id: Optional[int] = None, 
                 related: Optional[Dict[str, str]] = None) -> Links:
    """
    Crée les liens HATEOAS pour une ressource
    
    Args:
        base_url: URL de base de la ressource (ex: /api/users/me/holdings)
        resource_id: ID de la ressource (optionnel)
        related: Dictionnaire de ressources liées (optionnel)
    
    Returns:
        Objet Links avec les liens appropriés
    """
    links = Links()
    
    if resource_id:
        # Ressource individuelle
        links.self = Link(href=f"{base_url}/{resource_id}", method="GET", rel="self")
        links.update = Link(href=f"{base_url}/{resource_id}", method="PUT", rel="update")
        links.delete = Link(href=f"{base_url}/{resource_id}", method="DELETE", rel="delete")
        links.collection = Link(href=base_url, method="GET", rel="collection")
    else:
        # Collection
        links.self = Link(href=base_url, method="GET", rel="self")
        links.create = Link(href=base_url, method="POST", rel="create")
    
    # Ressources liées
    if related:
        links.related = {
            key: Link(href=url, method="GET", rel=key)
            for key, url in related.items()
        }
    
    return links

 


# ── Schémas pour compatibilité avec ancien router user.py ────────────

class UserDataResponse(BaseModel):
    """Schéma de réponse pour /api/user/data (ancien endpoint)"""
    user: UserResponse
    coins: List['WatchlistItemResponse']
    alerts: List[AlertResponse]


class CoinCreate(BaseModel):
    """Schéma pour créer un coin (ancien endpoint)"""
    coin_id: str = Field(..., description="ID CoinGecko")
    position: Optional[int] = Field(None, description="Position dans la liste")


class CoinResponse(BaseModel):
    """Schéma de réponse pour un coin (ancien endpoint)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    coin_id: str
    position: int
    created_at: datetime


class CoinsReorder(BaseModel):
    """Schéma pour réorganiser les coins (ancien endpoint)"""
    coin_ids: List[str] = Field(..., description="Liste ordonnée des coin_ids")
