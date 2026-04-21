"""
cache.py — Système de cache en mémoire

Implémente un cache simple avec TTL (Time To Live) pour réduire
les appels à l'API CoinGecko et améliorer les performances.
"""

import time
from typing import Any, Optional, Dict
from dataclasses import dataclass


@dataclass
class CacheEntry:
    """Entrée de cache avec données, timestamp et TTL"""
    data: Any
    timestamp: float
    ttl: int
    
    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée"""
        return time.time() - self.timestamp >= self.ttl
    
    def age(self) -> float:
        """Retourne l'âge de l'entrée en secondes"""
        return time.time() - self.timestamp


class MemoryCache:
    """
    Cache en mémoire avec support TTL
    
    Fonctionnalités :
    - Stockage clé-valeur avec expiration automatique
    - Récupération de données périmées (fallback en cas d'erreur API)
    - Statistiques de cache (hits/misses)
    """
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache si elle existe et n'est pas expirée
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur en cache ou None si absente/expirée
        """
        entry = self._cache.get(key)
        
        if not entry:
            self._misses += 1
            return None
        
        if entry.is_expired():
            self._misses += 1
            return None
        
        self._hits += 1
        return entry.data
    
    def get_stale(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache même si elle est expirée
        
        Utilisé comme fallback quand l'API CoinGecko retourne une erreur :
        mieux vaut des données périmées qu'une erreur visible.
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur en cache ou None si absente
        """
        entry = self._cache.get(key)
        return entry.data if entry else None
    
    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Stocke une valeur dans le cache avec son TTL
        
        Args:
            key: Clé de cache
            value: Valeur à stocker
            ttl: Durée de vie en secondes
        """
        self._cache[key] = CacheEntry(
            data=value,
            timestamp=time.time(),
            ttl=ttl
        )
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé de cache
            
        Returns:
            True si l'entrée existait, False sinon
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Vide complètement le cache"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def cleanup_expired(self) -> int:
        """
        Supprime toutes les entrées expirées du cache
        
        Returns:
            Nombre d'entrées supprimées
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache
        
        Returns:
            Dictionnaire avec les métriques du cache
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "keys": list(self._cache.keys()),
            "total_size_bytes": sum(
                len(str(entry.data)) for entry in self._cache.values()
            )
        }


# Instance globale du cache
cache = MemoryCache()

 