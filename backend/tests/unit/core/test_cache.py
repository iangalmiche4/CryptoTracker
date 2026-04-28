"""
test_cache.py — Tests unitaires pour core/cache.py

Tests couverts :
- Connexion Redis avec gestion d'erreurs
- Stockage et récupération de données
- Expiration des entrées (TTL)
- Suppression d'entrées
- Nettoyage du cache
- Statistiques du cache
- Fallback gracieux en cas d'erreur Redis

Principes appliqués :
- Isolation totale (mocks Redis)
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import redis
import json

from core.cache import RedisCache


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Connexion
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheConnection:
    """Tests pour la connexion Redis"""
    
    @patch('core.cache.redis.Redis')
    @patch('core.cache.redis.ConnectionPool')
    def test_init_should_connect_successfully(self, mock_pool, mock_redis):
        """
        GIVEN Redis est disponible
        WHEN RedisCache est initialisé
        THEN la connexion est établie
        """
        # Arrange
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client
        
        # Act
        cache = RedisCache()
        
        # Assert
        assert cache._available is True
        assert cache._client is not None
        mock_client.ping.assert_called_once()
    
    @patch('core.cache.redis.Redis')
    @patch('core.cache.redis.ConnectionPool')
    def test_init_should_handle_connection_error(self, mock_pool, mock_redis):
        """
        GIVEN Redis n'est pas disponible
        WHEN RedisCache est initialisé
        THEN le mode dégradé est activé
        """
        # Arrange
        mock_redis.side_effect = redis.ConnectionError("Connection refused")
        
        # Act
        cache = RedisCache()
        
        # Assert
        assert cache._available is False
        assert cache._client is None


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Get/Set
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheGetSet:
    """Tests pour les opérations get/set du cache"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Fixture qui fournit un client Redis mocké"""
        return Mock()
    
    @pytest.fixture
    def cache(self, mock_redis_client):
        """Fixture qui fournit un cache avec Redis mocké"""
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            cache = RedisCache()
            cache._client = mock_redis_client
            cache._available = True
            return cache
    
    def test_get_should_return_none_for_missing_key(self, cache, mock_redis_client):
        """
        GIVEN une clé inexistante
        WHEN get est appelé
        THEN None est retourné
        """
        # Arrange
        mock_redis_client.get.return_value = None
        
        # Act
        result = cache.get("nonexistent")
        
        # Assert
        assert result is None
        assert cache._misses == 1
    
    def test_set_and_get_should_store_and_retrieve_value(self, cache, mock_redis_client):
        """
        GIVEN une valeur stockée dans le cache
        WHEN get est appelé avec la même clé
        THEN la valeur est retournée
        """
        # Arrange
        test_data = {"test": "value"}
        mock_redis_client.get.return_value = json.dumps(test_data)
        
        # Act
        cache.set("key1", test_data, ttl=60)
        result = cache.get("key1")
        
        # Assert
        assert result == test_data
        assert cache._hits == 1
        mock_redis_client.setex.assert_called_once()
    
    def test_get_should_handle_json_decode_error(self, cache, mock_redis_client):
        """
        GIVEN des données corrompues dans Redis
        WHEN get est appelé
        THEN None est retourné
        """
        # Arrange
        mock_redis_client.get.return_value = "invalid json {"
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result is None
        assert cache._misses == 1
    
    def test_get_should_return_none_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN get est appelé
        THEN None est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result is None
        assert cache._misses == 1
    
    def test_set_should_return_false_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN set est appelé
        THEN False est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.set("key1", "value1", ttl=60)
        
        # Assert
        assert result is False


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Delete/Clear
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheDeleteClear:
    """Tests pour les opérations de suppression du cache"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Fixture qui fournit un client Redis mocké"""
        return Mock()
    
    @pytest.fixture
    def cache(self, mock_redis_client):
        """Fixture qui fournit un cache avec Redis mocké"""
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            cache = RedisCache()
            cache._client = mock_redis_client
            cache._available = True
            return cache
    
    def test_delete_should_remove_existing_entry(self, cache, mock_redis_client):
        """
        GIVEN une entrée dans le cache
        WHEN delete est appelé
        THEN l'entrée est supprimée et True est retourné
        """
        # Arrange
        mock_redis_client.delete.return_value = 1
        
        # Act
        result = cache.delete("key1")
        
        # Assert
        assert result is True
        mock_redis_client.delete.assert_called_once_with("key1")
    
    def test_delete_should_return_false_for_nonexistent_key(self, cache, mock_redis_client):
        """
        GIVEN une clé inexistante
        WHEN delete est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.delete.return_value = 0
        
        # Act
        result = cache.delete("nonexistent")
        
        # Assert
        assert result is False
    
    def test_clear_should_flush_database(self, cache, mock_redis_client):
        """
        GIVEN un cache avec des entrées
        WHEN clear est appelé
        THEN toutes les entrées sont supprimées
        """
        # Act
        result = cache.clear()
        
        # Assert
        assert result is True
        mock_redis_client.flushdb.assert_called_once()
        assert cache._hits == 0
        assert cache._misses == 0
        assert cache._errors == 0


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Statistics
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheStatistics:
    """Tests pour les statistiques du cache"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Fixture qui fournit un client Redis mocké"""
        client = Mock()
        client.info.return_value = {
            "connected_clients": 5,
            "total_commands_processed": 1000,
            "redis_version": "7.0.0",
            "used_memory_human": "1.5M",
            "used_memory_peak_human": "2.0M"
        }
        client.dbsize.return_value = 42
        return client
    
    @pytest.fixture
    def cache(self, mock_redis_client):
        """Fixture qui fournit un cache avec Redis mocké"""
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            cache = RedisCache()
            cache._client = mock_redis_client
            cache._available = True
            return cache
    
    def test_stats_should_track_hits_and_misses(self, cache, mock_redis_client):
        """
        GIVEN des opérations get sur le cache
        WHEN stats est appelé
        THEN les hits et misses sont comptabilisés
        """
        # Arrange
        cache._hits = 2
        cache._misses = 3
        
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["hits"] == 2
        assert stats["misses"] == 3
        assert stats["total_requests"] == 5
    
    def test_stats_should_calculate_hit_rate_correctly(self, cache, mock_redis_client):
        """
        GIVEN des hits et misses
        WHEN stats est appelé
        THEN le hit_rate est calculé correctement
        """
        # Arrange
        cache._hits = 1
        cache._misses = 1
        
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["hit_rate"] == "50.00%"
    
    def test_stats_should_include_redis_info(self, cache, mock_redis_client):
        """
        GIVEN Redis est disponible
        WHEN stats est appelé
        THEN les informations Redis sont incluses
        """
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["available"] is True
        assert stats["keys_count"] == 42
        assert "redis_version" in stats


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Utility Methods
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheUtility:
    """Tests pour les méthodes utilitaires du cache"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Fixture qui fournit un client Redis mocké"""
        return Mock()
    
    @pytest.fixture
    def cache(self, mock_redis_client):
        """Fixture qui fournit un cache avec Redis mocké"""
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            cache = RedisCache()
            cache._client = mock_redis_client
            cache._available = True
            return cache
    
    def test_ping_should_return_true_when_redis_available(self, cache, mock_redis_client):
        """
        GIVEN Redis est disponible
        WHEN ping est appelé
        THEN True est retourné
        """
        # Arrange
        mock_redis_client.ping.return_value = True
        
        # Act
        result = cache.ping()
        
        # Assert
        assert result is True
    
    def test_exists_should_check_key_existence(self, cache, mock_redis_client):
        """
        GIVEN une clé dans Redis
        WHEN exists est appelé
        THEN True est retourné
        """
        # Arrange
        mock_redis_client.exists.return_value = 1
        
        # Act
        result = cache.exists("key1")
        
        # Assert
        assert result is True
    
    def test_get_ttl_should_return_remaining_time(self, cache, mock_redis_client):
        """
        GIVEN une clé avec TTL
        WHEN get_ttl est appelé
        THEN le TTL restant est retourné
        """
        # Arrange
        mock_redis_client.ttl.return_value = 42
        
        # Act
        result = cache.get_ttl("key1")
        
        # Assert
        assert result == 42
    
    def test_keys_should_return_matching_keys(self, cache, mock_redis_client):
        """
        GIVEN des clés dans Redis
        WHEN keys est appelé avec un pattern
        THEN les clés correspondantes sont retournées
        """
        # Arrange
        mock_redis_client.keys.return_value = ["prices:btc", "prices:eth"]
        
        # Act
        result = cache.keys("prices:*")
        
        # Assert
        assert result == ["prices:btc", "prices:eth"]


# ══════════════════════════════════════════════════════════════════════
# TESTS : RedisCache - Error Handling
# ══════════════════════════════════════════════════════════════════════

class TestRedisCacheErrorHandling:
    """Tests pour la gestion d'erreurs du cache"""
    
    @pytest.fixture
    def mock_redis_client(self):
        """Fixture qui fournit un client Redis mocké"""
        return Mock()
    
    @pytest.fixture
    def cache(self, mock_redis_client):
        """Fixture qui fournit un cache avec Redis mocké"""
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            cache = RedisCache()
            cache._client = mock_redis_client
            cache._available = True
            return cache
    
    def test_get_should_handle_redis_error_gracefully(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur
        WHEN get est appelé
        THEN None est retourné et l'erreur est comptabilisée
        """
        # Arrange
        mock_redis_client.get.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result is None
        assert cache._errors == 1
    
    def test_set_should_handle_serialization_error(self, cache, mock_redis_client):
        """
        GIVEN des données non sérialisables
        WHEN set est appelé
        THEN False est retourné
        """
        # Arrange
        non_serializable = object()
        
        # Act
        result = cache.set("key1", non_serializable, ttl=60)
        
        # Assert
        assert result is False
    
    def test_get_stale_should_fallback_to_get(self, cache, mock_redis_client):
        """
        GIVEN une clé dans Redis
        WHEN get_stale est appelé
        THEN get est appelé (Redis ne garde pas les données expirées)
        """
        # Arrange
        test_data = {"test": "value"}
        mock_redis_client.get.return_value = json.dumps(test_data)
        
        # Act
        result = cache.get_stale("key1")
        
        # Assert
        assert result == test_data
        mock_redis_client.get.assert_called_once_with("key1")
    
    def test_cleanup_expired_should_return_zero(self, cache):
        """
        GIVEN un cache Redis
        WHEN cleanup_expired est appelé
        THEN 0 est retourné (Redis gère l'expiration automatiquement)
        """
        # Act
        result = cache.cleanup_expired()
        
        # Assert
        assert result == 0
    
    def test_close_should_close_connection(self, cache, mock_redis_client):
        """
        GIVEN une connexion Redis active
        WHEN close est appelé
        THEN la connexion est fermée
        """
        # Act
        cache.close()
        
        # Assert
        mock_redis_client.close.assert_called_once()
    
    def test_init_should_handle_generic_exception(self):
        """
        GIVEN une exception générique lors de la connexion
        WHEN RedisCache est initialisé
        THEN le mode dégradé est activé
        """
        # Arrange
        with patch('core.cache.redis.ConnectionPool') as mock_pool:
            mock_pool.side_effect = Exception("Unexpected error")
            
            # Act
            cache = RedisCache()
            
            # Assert
            assert cache._available is False
            assert cache._client is None
    
    def test_set_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du set
        WHEN set est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.setex.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.set("key1", {"test": "value"}, ttl=60)
        
        # Assert
        assert result is False
        assert cache._errors == 1
    
    def test_delete_should_return_false_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN delete est appelé
        THEN False est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.delete("key1")
        
        # Assert
        assert result is False
    
    def test_delete_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du delete
        WHEN delete est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.delete.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.delete("key1")
        
        # Assert
        assert result is False
        assert cache._errors == 1
    
    def test_clear_should_return_false_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN clear est appelé
        THEN False est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.clear()
        
        # Assert
        assert result is False
    
    def test_clear_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du clear
        WHEN clear est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.flushdb.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.clear()
        
        # Assert
        assert result is False
        assert cache._errors == 1
    
    def test_ping_should_return_false_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN ping est appelé
        THEN False est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.ping()
        
        # Assert
        assert result is False
    
    def test_ping_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du ping
        WHEN ping est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.ping.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.ping()
        
        # Assert
        assert result is False
        assert cache._errors == 1
    
    def test_get_ttl_should_return_none_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN get_ttl est appelé
        THEN None est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.get_ttl("key1")
        
        # Assert
        assert result is None
    
    def test_get_ttl_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du get_ttl
        WHEN get_ttl est appelé
        THEN None est retourné
        """
        # Arrange
        mock_redis_client.ttl.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.get_ttl("key1")
        
        # Assert
        assert result is None
        assert cache._errors == 1
    
    def test_exists_should_return_false_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN exists est appelé
        THEN False est retourné
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.exists("key1")
        
        # Assert
        assert result is False
    
    def test_exists_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du exists
        WHEN exists est appelé
        THEN False est retourné
        """
        # Arrange
        mock_redis_client.exists.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.exists("key1")
        
        # Assert
        assert result is False
        assert cache._errors == 1
    
    def test_keys_should_return_empty_list_when_redis_unavailable(self):
        """
        GIVEN Redis n'est pas disponible
        WHEN keys est appelé
        THEN une liste vide est retournée
        """
        # Arrange
        with patch('core.cache.redis.Redis') as mock_redis:
            mock_redis.side_effect = redis.ConnectionError()
            cache = RedisCache()
        
        # Act
        result = cache.keys("*")
        
        # Assert
        assert result == []
    
    def test_keys_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du keys
        WHEN keys est appelé
        THEN une liste vide est retournée
        """
        # Arrange
        mock_redis_client.keys.side_effect = redis.RedisError("Connection lost")
        
        # Act
        result = cache.keys("*")
        
        # Assert
        assert result == []
        assert cache._errors == 1
    
    def test_close_should_handle_redis_error(self, cache, mock_redis_client):
        """
        GIVEN Redis retourne une erreur lors du close
        WHEN close est appelé
        THEN l'erreur est gérée gracieusement
        """
        # Arrange
        mock_redis_client.close.side_effect = redis.RedisError("Connection lost")
        
        # Act
        cache.close()
        
        # Assert
        assert cache._errors == 1
    
    def test_safe_operation_should_handle_generic_exception(self, cache, mock_redis_client):
        """
        GIVEN une exception générique dans une opération Redis
        WHEN l'opération est exécutée
        THEN l'erreur est gérée gracieusement
        """
        # Arrange
        mock_redis_client.get.side_effect = Exception("Unexpected error")
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result is None
        assert cache._errors == 1

 
