"""
cache.py — Système de cache Redis

Implémente un cache distribué avec Redis pour :
- Réduire les appels à l'API CoinGecko
- Partager le cache entre plusieurs instances
- Persister le cache entre les redémarrages
- Gérer automatiquement les TTL et l'éviction

Architecture :
- RedisCache : Classe principale avec gestion d'erreurs robuste
- Fallback gracieux : Continue de fonctionner même si Redis est down
- Sérialisation JSON automatique
- Logging détaillé pour monitoring
"""

import redis
import json
import logging
from typing import Any, Optional, Dict
from contextlib import contextmanager

from config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Cache Redis avec gestion d'erreurs robuste et fallback
    
    Fonctionnalités :
    - Connexion Redis avec pool de connexions
    - TTL automatique par clé
    - Sérialisation/désérialisation JSON
    - Fallback gracieux si Redis est indisponible
    - Statistiques de cache (hits/misses)
    - Gestion des données périmées (stale data)
    """
    
    def __init__(self):
        """Initialise la connexion Redis avec pool de connexions"""
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._hits = 0
        self._misses = 0
        self._errors = 0
        
        self._connect()
    
    def _connect(self) -> None:
        """
        Établit la connexion à Redis avec gestion d'erreurs
        
        Utilise un pool de connexions pour de meilleures performances.
        Si Redis n'est pas disponible, l'application continue de fonctionner
        sans cache (mode dégradé).
        """
        try:
            # Configuration du pool de connexions
            pool = redis.ConnectionPool(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                decode_responses=settings.redis_decode_responses,
                max_connections=50,  # Pool de 50 connexions max
                retry_on_timeout=True,
                health_check_interval=30  # Vérification santé toutes les 30s
            )
            
            self._client = redis.Redis(connection_pool=pool)
            
            # Test de connexion
            self._client.ping()
            self._available = True
            
            logger.info(f"✅ Redis connected successfully at {settings.redis_host}:{settings.redis_port}")
            
        except redis.ConnectionError as e:
            logger.error(f"❌ Redis connection failed: {e}")
            logger.warning("⚠️  Running in degraded mode without cache")
            self._available = False
            self._client = None
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to Redis: {e}")
            self._available = False
            self._client = None
    
    @contextmanager
    def _safe_operation(self):
        """
        Context manager pour gérer les erreurs Redis de manière gracieuse
        
        Permet à l'application de continuer même si Redis échoue.
        Incrémente le compteur d'erreurs pour monitoring.
        """
        try:
            yield
        except redis.RedisError as e:
            self._errors += 1
            logger.error(f"❌ Redis error: {e}")
            # Ne pas propager l'erreur, continuer sans cache
        except Exception as e:
            self._errors += 1
            logger.error(f"❌ Unexpected cache error: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache Redis
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur désérialisée ou None si absente/expirée/erreur
        """
        if not self._available or not self._client:
            self._misses += 1
            return None
        
        with self._safe_operation():
            value = self._client.get(key)
            
            if value is None:
                self._misses += 1
                return None
            
            self._hits += 1
            
            # Désérialiser le JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error for key {key}: {e}")
                self._misses += 1
                return None
        
        # En cas d'erreur dans safe_operation
        self._misses += 1
        return None
    
    def get_stale(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur du cache même si elle est expirée
        
        Utilisé comme fallback quand l'API CoinGecko retourne une erreur.
        Redis ne stocke pas les données expirées, donc cette méthode
        est équivalente à get() pour Redis (contrairement au MemoryCache).
        
        Args:
            key: Clé de cache
            
        Returns:
            Valeur en cache ou None si absente
        """
        # Pour Redis, les données expirées sont automatiquement supprimées
        # On retourne donc simplement get() qui peut retourner des données
        # récentes si elles existent encore
        return self.get(key)
    
    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Stocke une valeur dans Redis avec TTL
        
        Args:
            key: Clé de cache
            value: Valeur à stocker (sera sérialisée en JSON)
            ttl: Durée de vie en secondes
            
        Returns:
            True si succès, False sinon
        """
        if not self._available or not self._client:
            return False
        
        with self._safe_operation():
            # Sérialiser en JSON
            try:
                serialized = json.dumps(value, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.error(f"❌ JSON encode error for key {key}: {e}")
                return False
            
            # Stocker avec TTL
            self._client.setex(key, ttl, serialized)
            return True
        
        return False
    
    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé de cache
            
        Returns:
            True si l'entrée existait, False sinon
        """
        if not self._available or not self._client:
            return False
        
        with self._safe_operation():
            result = self._client.delete(key)
            return result > 0
        
        return False
    
    def clear(self) -> bool:
        """
        Vide complètement le cache Redis
        
        ⚠️  Attention : Supprime TOUTES les clés de la base Redis configurée
        
        Returns:
            True si succès, False sinon
        """
        if not self._available or not self._client:
            return False
        
        with self._safe_operation():
            self._client.flushdb()
            self._hits = 0
            self._misses = 0
            self._errors = 0
            logger.info("🗑️  Redis cache cleared")
            return True
        
        return False
    
    def cleanup_expired(self) -> int:
        """
        Nettoyage des entrées expirées
        
        Note : Redis gère automatiquement l'expiration des clés avec TTL.
        Cette méthode existe pour compatibilité avec l'ancienne interface
        mais ne fait rien car Redis s'en charge automatiquement.
        
        Returns:
            0 (Redis gère l'expiration automatiquement)
        """
        # Redis gère automatiquement l'expiration via TTL
        # Pas besoin de cleanup manuel
        return 0
    
    def stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache
        
        Returns:
            Dictionnaire avec les métriques du cache
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            "available": self._available,
            "hits": self._hits,
            "misses": self._misses,
            "errors": self._errors,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests
        }
        
        # Ajouter les stats Redis si disponible
        if self._available and self._client:
            with self._safe_operation():
                info = self._client.info("stats")
                redis_info = self._client.info("memory")
                
                stats.update({
                    "redis_version": self._client.info("server").get("redis_version", "unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "unknown"),
                    "used_memory_peak_human": redis_info.get("used_memory_peak_human", "unknown"),
                    "keys_count": self._client.dbsize()
                })
        
        return stats
    
    def ping(self) -> bool:
        """
        Vérifie que Redis est accessible
        
        Returns:
            True si Redis répond, False sinon
        """
        if not self._available or not self._client:
            return False
        
        with self._safe_operation():
            return self._client.ping()
        
        return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Récupère le TTL restant d'une clé
        
        Args:
            key: Clé de cache
            
        Returns:
            TTL en secondes, -1 si pas de TTL, -2 si clé n'existe pas, None si erreur
        """
        if not self._available or not self._client:
            return None
        
        with self._safe_operation():
            return self._client.ttl(key)
        
        return None
    
    def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans le cache
        
        Args:
            key: Clé de cache
            
        Returns:
            True si la clé existe, False sinon
        """
        if not self._available or not self._client:
            return False
        
        with self._safe_operation():
            return self._client.exists(key) > 0
        
        return False
    
    def keys(self, pattern: str = "*") -> list[str]:
        """
        Liste les clés correspondant à un pattern
        
        ⚠️  Attention : Opération coûteuse en production, utiliser avec parcimonie
        
        Args:
            pattern: Pattern de recherche (ex: "prices:*")
            
        Returns:
            Liste des clés correspondantes
        """
        if not self._available or not self._client:
            return []
        
        with self._safe_operation():
            return self._client.keys(pattern)
        
        return []
    
    def close(self) -> None:
        """Ferme proprement la connexion Redis"""
        if self._client:
            with self._safe_operation():
                self._client.close()
                logger.info("🔌 Redis connection closed")


# Instance globale du cache Redis
cache = RedisCache()

 
