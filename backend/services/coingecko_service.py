"""
coingecko_service.py — Service pour interagir avec l'API CoinGecko

Responsabilités :
- Effectuer les requêtes HTTP vers CoinGecko
- Gérer le cache des réponses
- Normaliser les données pour le frontend
- Gérer les erreurs (rate limit, timeout, etc.)
"""

import httpx
import logging
from datetime import datetime, timezone
from typing import Dict, List

from config import settings
from core.cache import cache
from core.exceptions import (
    RateLimitException,
    TimeoutException,
    APIException
)

logger = logging.getLogger(__name__)


# ── Constantes ────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "CryptoTracker/1.0 (educational project)",
    "Accept": "application/json",
}


# ── Service CoinGecko ─────────────────────────────────────────────────

class CoinGeckoService:
    """Service pour interagir avec l'API CoinGecko"""
    
    def __init__(self):
        self.base_url = settings.coingecko_url
        self.timeout = settings.api_timeout
        self.detail_timeout = settings.detail_timeout
    
    async def get_prices(self, coins: str) -> Dict:
        """
        Récupère les prix et métriques de marché pour une liste de coins
        
        Args:
            coins: Liste de coin_ids séparés par des virgules (ex: "bitcoin,ethereum")
        
        Returns:
            Dictionnaire avec les prix et métriques
        
        Raises:
            RateLimitException: Si le rate limit est atteint
            TimeoutException: Si la requête timeout
            APIException: Pour les autres erreurs API
        """
        # Normaliser les coins (tri alphabétique pour cache canonique)
        normalized = ",".join(sorted(coins.split(",")))
        cache_key = f"prices:{normalized}"
        
        # Vérifier le cache
        if cached := cache.get(cache_key):
            logger.info(f"✅ Cache HIT for prices: {coins}")
            return cached
        
        logger.info(f"❌ Cache MISS for prices: {coins} - Fetching from CoinGecko")
        
        try:
            async with httpx.AsyncClient(headers=HEADERS) as client:
                response = await client.get(
                    f"{self.base_url}/simple/price",
                    params={
                        "ids": normalized,
                        "vs_currencies": "usd",
                        "include_24hr_change": "true",
                        "include_market_cap": "true",
                        "include_24hr_vol": "true",
                    },
                    timeout=self.timeout
                )
            
            # Gérer les erreurs
            if response.status_code == 429:
                logger.warning(f"⚠️  CoinGecko rate limit (429) for prices: {coins}")
                # Retourner données périmées si disponibles
                if stale := cache.get_stale(cache_key):
                    return stale
                raise RateLimitException("Rate limit CoinGecko — réessaie dans quelques secondes")
            
            if response.status_code != 200:
                logger.error(f"❌ CoinGecko error {response.status_code} for prices: {coins}")
                if stale := cache.get_stale(cache_key):
                    return stale
                raise APIException(response.status_code, "Erreur CoinGecko")
            
            data = response.json()
            cache.set(cache_key, data, settings.prices_ttl)
            logger.info(f"✅ Successfully fetched and cached prices for: {coins}")
            return data
        
        except httpx.TimeoutException:
            logger.error(f"⏱️  Timeout fetching prices for: {coins}")
            if stale := cache.get_stale(cache_key):
                return stale
            raise TimeoutException("Timeout CoinGecko — réessaie dans quelques instants")
    
    async def search_coins(self, query: str) -> List[Dict]:
        """
        Recherche des coins par nom ou symbole
        
        Args:
            query: Terme de recherche
        
        Returns:
            Liste de coins correspondants (max 6)
        
        Raises:
            RateLimitException: Si le rate limit est atteint
            TimeoutException: Si la requête timeout
        """
        cache_key = f"search:{query.lower().strip()}"
        
        if cached := cache.get(cache_key):
            logger.info(f"✅ Cache HIT for search: {query}")
            return cached
        
        logger.info(f"❌ Cache MISS for search: {query} - Fetching from CoinGecko")
        
        try:
            async with httpx.AsyncClient(headers=HEADERS) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={"query": query},
                    timeout=self.timeout
                )
            
            if response.status_code == 429:
                logger.warning(f"⚠️  CoinGecko rate limit (429) for search: {query}")
                return cache.get_stale(cache_key) or []
            
            if response.status_code != 200:
                logger.error(f"❌ CoinGecko error {response.status_code} for search: {query}")
                return cache.get_stale(cache_key) or []
            
            # Filtrer et limiter les résultats
            coins = response.json().get("coins", [])[:6]
            data = [
                {"id": c["id"], "name": c["name"], "symbol": c["symbol"]}
                for c in coins
            ]
            
            cache.set(cache_key, data, settings.search_ttl)
            logger.info(f"✅ Successfully fetched and cached search results for: {query}")
            return data
        
        except httpx.TimeoutException:
            logger.error(f"⏱️  Timeout searching for: {query}")
            return cache.get_stale(cache_key) or []
    
    async def get_history(self, coin_id: str, days: int = 7) -> List[Dict]:
        """
        Récupère l'historique des prix d'un coin
        
        Args:
            coin_id: ID CoinGecko du coin
            days: Nombre de jours d'historique
        
        Returns:
            Liste de points de données {date, price}
        
        Raises:
            RateLimitException: Si le rate limit est atteint
            TimeoutException: Si la requête timeout
        """
        cache_key = f"history:{coin_id}:{days}"
        
        if cached := cache.get(cache_key):
            logger.info(f"✅ Cache HIT for history: {coin_id} ({days} days)")
            return cached
        
        logger.info(f"❌ Cache MISS for history: {coin_id} ({days} days) - Fetching from CoinGecko")
        
        try:
            async with httpx.AsyncClient(headers=HEADERS) as client:
                response = await client.get(
                    f"{self.base_url}/coins/{coin_id}/market_chart",
                    params={"vs_currency": "usd", "days": days, "interval": "daily"},
                    timeout=self.timeout
                )
            
            if response.status_code == 429:
                logger.warning(f"⚠️  CoinGecko rate limit (429) for history: {coin_id}")
                return cache.get_stale(cache_key) or []
            
            if response.status_code != 200:
                logger.error(f"❌ CoinGecko error {response.status_code} for history: {coin_id}")
                return cache.get_stale(cache_key) or []
            
            raw = response.json().get("prices", [])
            
            # Transformer les données pour Recharts
            data = [
                {
                    "date": datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).strftime("%d/%m"),
                    "price": round(p[1], 2),
                }
                for p in raw
            ]
            
            cache.set(cache_key, data, settings.history_ttl)
            logger.info(f"✅ Successfully fetched and cached history for: {coin_id} ({days} days)")
            return data
        
        except httpx.TimeoutException:
            logger.error(f"⏱️  Timeout fetching history for: {coin_id}")
            return cache.get_stale(cache_key) or []
    
    async def get_detail(self, coin_id: str) -> Dict:
        """
        Récupère les informations détaillées d'un coin
        
        Args:
            coin_id: ID CoinGecko du coin
        
        Returns:
            Dictionnaire avec les informations détaillées
        
        Raises:
            RateLimitException: Si le rate limit est atteint
            TimeoutException: Si la requête timeout
        """
        cache_key = f"detail:{coin_id}"
        
        if cached := cache.get(cache_key):
            logger.info(f"✅ Cache HIT for detail: {coin_id}")
            return cached
        
        logger.info(f"❌ Cache MISS for detail: {coin_id} - Fetching from CoinGecko")
        
        try:
            async with httpx.AsyncClient(headers=HEADERS) as client:
                response = await client.get(
                    f"{self.base_url}/coins/{coin_id}",
                    params={
                        "localization": "false",
                        "tickers": "false",
                        "community_data": "true",
                        "developer_data": "false",
                    },
                    timeout=self.detail_timeout
                )
            
            if response.status_code == 429:
                logger.warning(f"⚠️  CoinGecko rate limit (429) for detail: {coin_id}")
                return cache.get_stale(cache_key) or {}
            
            if response.status_code != 200:
                logger.error(f"❌ CoinGecko error {response.status_code} for detail: {coin_id}")
                return cache.get_stale(cache_key) or {}
            
            d = response.json()
            mr = d.get("market_data", {})
            
            # Construire l'objet métier
            data = {
                "id": d["id"],
                "name": d["name"],
                "symbol": d["symbol"].upper(),
                "description": d.get("description", {}).get("en", "")[:600],
                "image": d.get("image", {}).get("large", ""),
                "links": {
                    "homepage": (d.get("links", {}).get("homepage", [""]))[0],
                    "twitter": d.get("links", {}).get("twitter_screen_name", ""),
                    "subreddit": d.get("links", {}).get("subreddit_url", ""),
                },
                "market": {
                    "price_usd": mr.get("current_price", {}).get("usd"),
                    "market_cap": mr.get("market_cap", {}).get("usd"),
                    "fully_diluted_val": mr.get("fully_diluted_valuation", {}).get("usd"),
                    "volume_24h": mr.get("total_volume", {}).get("usd"),
                    "change_24h": mr.get("price_change_percentage_24h"),
                    "change_7d": mr.get("price_change_percentage_7d"),
                    "change_30d": mr.get("price_change_percentage_30d"),
                    "ath": mr.get("ath", {}).get("usd"),
                    "ath_change_pct": mr.get("ath_change_percentage", {}).get("usd"),
                    "circulating_supply": mr.get("circulating_supply"),
                    "total_supply": mr.get("total_supply"),
                    "max_supply": mr.get("max_supply"),
                },
                "sentiment_up_pct": d.get("sentiment_votes_up_percentage"),
            }
            
            cache.set(cache_key, data, settings.detail_ttl)
            logger.info(f"✅ Successfully fetched and cached details for: {coin_id}")
            return data
        
        except httpx.TimeoutException:
            logger.error(f"⏱️  Timeout fetching details for: {coin_id}")
            return cache.get_stale(cache_key) or {}


# Instance globale du service
coingecko_service = CoinGeckoService()

 