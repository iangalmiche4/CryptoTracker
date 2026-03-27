"""
test_cache.py — Tests unitaires pour core/cache.py

Tests couverts :
- Stockage et récupération de données
- Expiration des entrées (TTL)
- Récupération de données périmées (stale)
- Suppression d'entrées
- Nettoyage du cache
- Statistiques du cache

Principes appliqués :
- Isolation totale (pas de dépendances externes)
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites
"""

import pytest
import time
from unittest.mock import patch

from core.cache import MemoryCache, CacheEntry


# ══════════════════════════════════════════════════════════════════════
# TESTS : CacheEntry
# ══════════════════════════════════════════════════════════════════════

class TestCacheEntry:
    """Tests pour la classe CacheEntry"""
    
    def test_is_expired_should_return_false_for_fresh_entry(self):
        """
        GIVEN une entrée de cache récente
        WHEN is_expired est appelé
        THEN False est retourné
        """
        # Arrange
        entry = CacheEntry(data="test", timestamp=time.time(), ttl=60)
        
        # Act
        result = entry.is_expired()
        
        # Assert
        assert result is False
    
    def test_is_expired_should_return_true_for_old_entry(self):
        """
        GIVEN une entrée de cache expirée
        WHEN is_expired est appelé
        THEN True est retourné
        """
        # Arrange
        old_timestamp = time.time() - 120  # 2 minutes ago
        entry = CacheEntry(data="test", timestamp=old_timestamp, ttl=60)
        
        # Act
        result = entry.is_expired()
        
        # Assert
        assert result is True
    
    def test_age_should_return_seconds_since_creation(self):
        """
        GIVEN une entrée de cache
        WHEN age est appelé
        THEN l'âge en secondes est retourné
        """
        # Arrange
        timestamp = time.time() - 10  # 10 seconds ago
        entry = CacheEntry(data="test", timestamp=timestamp, ttl=60)
        
        # Act
        age = entry.age()
        
        # Assert
        assert 9 <= age <= 11  # Allow small time variance


# ══════════════════════════════════════════════════════════════════════
# TESTS : MemoryCache - Get/Set
# ══════════════════════════════════════════════════════════════════════

class TestMemoryCacheGetSet:
    """Tests pour les opérations get/set du cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture qui fournit un cache vide"""
        return MemoryCache()
    
    def test_get_should_return_none_for_missing_key(self, cache):
        """
        GIVEN un cache vide
        WHEN get est appelé avec une clé inexistante
        THEN None est retourné
        """
        # Act
        result = cache.get("nonexistent")
        
        # Assert
        assert result is None
    
    def test_set_and_get_should_store_and_retrieve_value(self, cache):
        """
        GIVEN une valeur stockée dans le cache
        WHEN get est appelé avec la même clé
        THEN la valeur est retournée
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result == "value1"
    
    def test_get_should_return_none_for_expired_entry(self, cache):
        """
        GIVEN une entrée expirée dans le cache
        WHEN get est appelé
        THEN None est retourné
        """
        # Arrange
        with patch('time.time', return_value=1000):
            cache.set("key1", "value1", ttl=10)
        
        # Act - Simulate time passing
        with patch('time.time', return_value=1020):  # 20 seconds later
            result = cache.get("key1")
        
        # Assert
        assert result is None
    
    def test_get_stale_should_return_expired_data(self, cache):
        """
        GIVEN une entrée expirée dans le cache
        WHEN get_stale est appelé
        THEN les données périmées sont retournées
        """
        # Arrange
        with patch('time.time', return_value=1000):
            cache.set("key1", "stale_value", ttl=10)
        
        # Act - Simulate time passing
        with patch('time.time', return_value=1020):  # 20 seconds later
            result = cache.get_stale("key1")
        
        # Assert
        assert result == "stale_value"
    
    def test_get_stale_should_return_none_for_missing_key(self, cache):
        """
        GIVEN un cache vide
        WHEN get_stale est appelé
        THEN None est retourné
        """
        # Act
        result = cache.get_stale("nonexistent")
        
        # Assert
        assert result is None
    
    def test_set_should_overwrite_existing_value(self, cache):
        """
        GIVEN une clé existante dans le cache
        WHEN set est appelé avec la même clé
        THEN la valeur est écrasée
        """
        # Arrange
        cache.set("key1", "old_value", ttl=60)
        
        # Act
        cache.set("key1", "new_value", ttl=60)
        result = cache.get("key1")
        
        # Assert
        assert result == "new_value"


# ══════════════════════════════════════════════════════════════════════
# TESTS : MemoryCache - Delete/Clear
# ══════════════════════════════════════════════════════════════════════

class TestMemoryCacheDeleteClear:
    """Tests pour les opérations de suppression du cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture qui fournit un cache vide"""
        return MemoryCache()
    
    def test_delete_should_remove_existing_entry(self, cache):
        """
        GIVEN une entrée dans le cache
        WHEN delete est appelé
        THEN l'entrée est supprimée et True est retourné
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        
        # Act
        result = cache.delete("key1")
        
        # Assert
        assert result is True
        assert cache.get("key1") is None
    
    def test_delete_should_return_false_for_nonexistent_key(self, cache):
        """
        GIVEN un cache vide
        WHEN delete est appelé avec une clé inexistante
        THEN False est retourné
        """
        # Act
        result = cache.delete("nonexistent")
        
        # Assert
        assert result is False
    
    def test_clear_should_empty_cache(self, cache):
        """
        GIVEN un cache avec plusieurs entrées
        WHEN clear est appelé
        THEN toutes les entrées sont supprimées
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        cache.set("key3", "value3", ttl=60)
        
        # Act
        cache.clear()
        
        # Assert
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None
    
    def test_clear_should_reset_statistics(self, cache):
        """
        GIVEN un cache avec des statistiques
        WHEN clear est appelé
        THEN les statistiques sont réinitialisées
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        # Act
        cache.clear()
        stats = cache.stats()
        
        # Assert
        assert stats["hits"] == 0
        assert stats["misses"] == 0


# ══════════════════════════════════════════════════════════════════════
# TESTS : MemoryCache - Cleanup
# ══════════════════════════════════════════════════════════════════════

class TestMemoryCacheCleanup:
    """Tests pour le nettoyage du cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture qui fournit un cache vide"""
        return MemoryCache()
    
    def test_cleanup_expired_should_remove_only_expired_entries(self, cache):
        """
        GIVEN un cache avec des entrées expirées et valides
        WHEN cleanup_expired est appelé
        THEN seules les entrées expirées sont supprimées
        """
        # Arrange
        with patch('time.time', return_value=1000):
            cache.set("fresh1", "value1", ttl=100)
            cache.set("fresh2", "value2", ttl=100)
            cache.set("expired1", "value3", ttl=10)
            cache.set("expired2", "value4", ttl=10)
        
        # Act - Simulate time passing
        with patch('time.time', return_value=1050):  # 50 seconds later
            removed_count = cache.cleanup_expired()
        
        # Assert
        assert removed_count == 2
        assert cache.get_stale("fresh1") == "value1"
        assert cache.get_stale("fresh2") == "value2"
        assert cache.get_stale("expired1") is None
        assert cache.get_stale("expired2") is None
    
    def test_cleanup_expired_should_return_zero_for_empty_cache(self, cache):
        """
        GIVEN un cache vide
        WHEN cleanup_expired est appelé
        THEN 0 est retourné
        """
        # Act
        removed_count = cache.cleanup_expired()
        
        # Assert
        assert removed_count == 0
    
    def test_cleanup_expired_should_return_zero_when_no_expired_entries(self, cache):
        """
        GIVEN un cache avec seulement des entrées valides
        WHEN cleanup_expired est appelé
        THEN 0 est retourné
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        
        # Act
        removed_count = cache.cleanup_expired()
        
        # Assert
        assert removed_count == 0


# ══════════════════════════════════════════════════════════════════════
# TESTS : MemoryCache - Statistics
# ══════════════════════════════════════════════════════════════════════

class TestMemoryCacheStatistics:
    """Tests pour les statistiques du cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture qui fournit un cache vide"""
        return MemoryCache()
    
    def test_stats_should_track_hits_and_misses(self, cache):
        """
        GIVEN des opérations get sur le cache
        WHEN stats est appelé
        THEN les hits et misses sont comptabilisés
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        
        # Act
        cache.get("key1")  # Hit
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        cache.get("key3")  # Miss
        cache.get("key3")  # Miss
        
        stats = cache.stats()
        
        # Assert
        assert stats["hits"] == 2
        assert stats["misses"] == 3
    
    def test_stats_should_calculate_hit_rate_correctly(self, cache):
        """
        GIVEN des hits et misses
        WHEN stats est appelé
        THEN le hit_rate est calculé correctement
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["hit_rate"] == "50.00%"
    
    def test_stats_should_return_zero_hit_rate_for_empty_cache(self, cache):
        """
        GIVEN un cache sans requêtes
        WHEN stats est appelé
        THEN le hit_rate est 0%
        """
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["hit_rate"] == "0.00%"
        assert stats["hits"] == 0
        assert stats["misses"] == 0
    
    def test_stats_should_list_all_cache_keys(self, cache):
        """
        GIVEN un cache avec plusieurs entrées
        WHEN stats est appelé
        THEN toutes les clés sont listées
        """
        # Arrange
        cache.set("key1", "value1", ttl=60)
        cache.set("key2", "value2", ttl=60)
        cache.set("key3", "value3", ttl=60)
        
        # Act
        stats = cache.stats()
        
        # Assert
        assert set(stats["keys"]) == {"key1", "key2", "key3"}
        assert stats["entries"] == 3
    
    def test_stats_should_calculate_total_size(self, cache):
        """
        GIVEN un cache avec des données
        WHEN stats est appelé
        THEN la taille totale est calculée
        """
        # Arrange
        cache.set("key1", "short", ttl=60)
        cache.set("key2", "a much longer value", ttl=60)
        
        # Act
        stats = cache.stats()
        
        # Assert
        assert stats["total_size_bytes"] > 0
        assert isinstance(stats["total_size_bytes"], int)


# ══════════════════════════════════════════════════════════════════════
# TESTS : MemoryCache - Edge Cases
# ══════════════════════════════════════════════════════════════════════

class TestMemoryCacheEdgeCases:
    """Tests pour les cas limites du cache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture qui fournit un cache vide"""
        return MemoryCache()
    
    def test_cache_should_handle_none_values(self, cache):
        """
        GIVEN une valeur None stockée
        WHEN get est appelé
        THEN None est retourné (mais c'est la valeur, pas une absence)
        """
        # Arrange
        cache.set("key1", None, ttl=60)
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result is None
        # Verify it's actually in cache
        assert "key1" in cache.stats()["keys"]
    
    def test_cache_should_handle_complex_data_types(self, cache):
        """
        GIVEN des types de données complexes
        WHEN ils sont stockés et récupérés
        THEN les données sont préservées
        """
        # Arrange
        complex_data = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3)
        }
        cache.set("complex", complex_data, ttl=60)
        
        # Act
        result = cache.get("complex")
        
        # Assert
        assert result == complex_data
        assert result["list"] == [1, 2, 3]
    
    def test_cache_should_handle_zero_ttl(self, cache):
        """
        GIVEN un TTL de 0
        WHEN l'entrée est créée
        THEN elle est immédiatement expirée
        """
        # Arrange & Act
        cache.set("key1", "value1", ttl=0)
        
        # Assert
        assert cache.get("key1") is None
        assert cache.get_stale("key1") == "value1"
    
    def test_cache_should_handle_large_ttl(self, cache):
        """
        GIVEN un TTL très grand
        WHEN l'entrée est créée
        THEN elle reste valide
        """
        # Arrange
        cache.set("key1", "value1", ttl=999999)
        
        # Act
        result = cache.get("key1")
        
        # Assert
        assert result == "value1"

