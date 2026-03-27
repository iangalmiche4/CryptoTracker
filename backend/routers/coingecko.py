"""
coingecko.py — Routes pour l'API CoinGecko

Endpoints :
  GET /api/prices : Prix et métriques de marché
  GET /api/search : Recherche de coins
  GET /api/history/{coin_id} : Historique des prix
  GET /api/detail/{coin_id} : Informations détaillées
  GET /api/cache/stats : Statistiques du cache (monitoring)
"""

from fastapi import APIRouter, HTTPException
import logging

from services.coingecko_service import coingecko_service
from core.cache import cache
from core.exceptions import (
    RateLimitException,
    TimeoutException,
    APIException,
    to_http_exception
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CoinGecko"])


@router.get("/api/prices")
async def get_prices(coins: str = "bitcoin,ethereum,solana"):
    """
    Retourne les prix en USD et métriques de marché pour une liste de coins
    
    Args:
        coins: Liste de coin_ids séparés par des virgules
    
    Returns:
        Dictionnaire avec les prix et métriques
    
    Raises:
        HTTPException 429: Rate limit atteint
        HTTPException 504: Timeout
        HTTPException 502: Erreur API
    """
    try:
        return await coingecko_service.get_prices(coins)
    except (RateLimitException, TimeoutException, APIException) as e:
        raise to_http_exception(e)
    except Exception as e:
        logger.error(f"Unexpected error in get_prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/api/search")
async def search_coins(q: str):
    """
    Recherche des coins par nom ou symbole
    
    Args:
        q: Terme de recherche
    
    Returns:
        Liste de coins correspondants (max 6)
    """
    try:
        return await coingecko_service.search_coins(q)
    except Exception as e:
        logger.error(f"Unexpected error in search_coins: {str(e)}")
        # Retourner liste vide plutôt qu'une erreur pour la recherche
        return []


@router.get("/api/history/{coin_id}")
async def get_history(coin_id: str, days: int = 7):
    """
    Retourne l'historique des prix d'un coin
    
    Args:
        coin_id: ID CoinGecko du coin
        days: Nombre de jours d'historique (défaut: 7)
    
    Returns:
        Liste de points de données {date, price}
    """
    try:
        return await coingecko_service.get_history(coin_id, days)
    except Exception as e:
        logger.error(f"Unexpected error in get_history: {str(e)}")
        # Retourner liste vide plutôt qu'une erreur
        return []


@router.get("/api/detail/{coin_id}")
async def get_detail(coin_id: str):
    """
    Retourne les informations détaillées d'un coin
    
    Args:
        coin_id: ID CoinGecko du coin
    
    Returns:
        Dictionnaire avec les informations détaillées
    """
    try:
        return await coingecko_service.get_detail(coin_id)
    except Exception as e:
        logger.error(f"Unexpected error in get_detail: {str(e)}")
        # Retourner objet vide plutôt qu'une erreur
        return {}


@router.get("/api/cache/stats")
async def cache_stats():
    """
    Endpoint de monitoring : retourne les statistiques du cache
    
    ⚠️  En production, cet endpoint devrait être protégé par authentification
    ou désactivé pour ne pas exposer les détails internes de l'API.
    
    Returns:
        Statistiques du cache (nombre d'entrées, hits/misses, etc.)
    """
    logger.info("📊 Cache stats requested")
    stats = cache.stats()
    stats["cache_config"] = {
        "prices_ttl": 30,
        "search_ttl": 300,
        "history_ttl": 300,
        "detail_ttl": 120,
    }
    return stats

 