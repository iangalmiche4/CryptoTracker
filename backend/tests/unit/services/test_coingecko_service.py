"""
test_coingecko_service.py — Tests unitaires pour services/coingecko_service.py

Tests couverts :
- Récupération des prix (get_prices)
- Recherche de coins (search_coins)
- Historique des prix (get_history)
- Détails d'un coin (get_detail)
- Gestion du cache
- Gestion des erreurs (rate limit, timeout, erreurs API)

Principes appliqués :
- Isolation totale avec mocks (pas d'appels HTTP réels)
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites et erreurs
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import httpx

from services.coingecko_service import CoinGeckoService
from core.exceptions import RateLimitException, TimeoutException, APIException


# ══════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_settings():
    """Fixture pour mocker les settings"""
    with patch('services.coingecko_service.settings') as mock:
        mock.coingecko_url = "https://api.coingecko.com/api/v3"
        mock.api_timeout = 10.0
        mock.detail_timeout = 15.0
        mock.prices_ttl = 30
        mock.search_ttl = 300
        mock.history_ttl = 300
        mock.detail_ttl = 120
        yield mock


@pytest.fixture
def mock_cache():
    """Fixture pour mocker le cache"""
    with patch('services.coingecko_service.cache') as mock:
        mock.get = Mock(return_value=None)
        mock.set = Mock()
        mock.get_stale = Mock(return_value=None)
        yield mock


@pytest.fixture
def service(mock_settings):
    """Fixture pour créer une instance du service"""
    return CoinGeckoService()


@pytest.fixture
def mock_httpx_client():
    """Fixture pour mocker httpx.AsyncClient"""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    return mock_client, mock_response


# ══════════════════════════════════════════════════════════════════════
# TESTS : get_prices
# ══════════════════════════════════════════════════════════════════════

class TestGetPrices:
    """Tests pour la méthode get_prices"""
    
    @pytest.mark.asyncio
    async def test_get_prices_should_return_cached_data_when_available(
        self, service, mock_cache
    ):
        """
        GIVEN des données en cache
        WHEN get_prices est appelé
        THEN les données du cache sont retournées sans appel API
        """
        # Arrange
        coins = "bitcoin,ethereum"
        cached_data = {
            "bitcoin": {"usd": 50000, "usd_24h_change": 2.5},
            "ethereum": {"usd": 3000, "usd_24h_change": 1.8}
        }
        mock_cache.get.return_value = cached_data
        
        # Act
        result = await service.get_prices(coins)
        
        # Assert
        assert result == cached_data
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_prices_should_fetch_from_api_when_cache_miss(
        self, service, mock_cache
    ):
        """
        GIVEN pas de données en cache
        WHEN get_prices est appelé
        THEN les données sont récupérées de l'API et mises en cache
        """
        # Arrange
        coins = "bitcoin"
        api_data = {"bitcoin": {"usd": 50000, "usd_24h_change": 2.5}}
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=api_data)
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_prices(coins)
        
        # Assert
        assert result == api_data
        mock_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_prices_should_normalize_coin_ids_for_cache(
        self, service, mock_cache
    ):
        """
        GIVEN des coin_ids dans un ordre différent
        WHEN get_prices est appelé
        THEN les IDs sont triés alphabétiquement pour le cache
        """
        # Arrange
        coins = "ethereum,bitcoin,cardano"
        expected_normalized = "bitcoin,cardano,ethereum"
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            await service.get_prices(coins)
        
        # Assert
        # Vérifier que le cache.get a été appelé avec les IDs normalisés
        cache_key = f"prices:{expected_normalized}"
        mock_cache.get.assert_called_with(cache_key)
    
    @pytest.mark.asyncio
    async def test_get_prices_should_raise_rate_limit_exception_on_429(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne 429 (rate limit)
        WHEN get_prices est appelé
        THEN RateLimitException est levée
        """
        # Arrange
        coins = "bitcoin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(RateLimitException):
                await service.get_prices(coins)
    
    @pytest.mark.asyncio
    async def test_get_prices_should_return_stale_data_on_429_if_available(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne 429 et des données périmées existent
        WHEN get_prices est appelé
        THEN les données périmées sont retournées
        """
        # Arrange
        coins = "bitcoin"
        stale_data = {"bitcoin": {"usd": 49000}}
        
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_prices(coins)
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_prices_should_raise_timeout_exception_on_timeout(
        self, service, mock_cache
    ):
        """
        GIVEN l'API timeout
        WHEN get_prices est appelé
        THEN TimeoutException est levée
        """
        # Arrange
        coins = "bitcoin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Timeout")
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(TimeoutException):
                await service.get_prices(coins)
    
    @pytest.mark.asyncio
    async def test_get_prices_should_raise_api_exception_on_non_200_status(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne un code d'erreur (500, 503, etc.)
        WHEN get_prices est appelé
        THEN APIException est levée
        """
        # Arrange
        coins = "bitcoin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act & Assert
            with pytest.raises(APIException):
                await service.get_prices(coins)


# ══════════════════════════════════════════════════════════════════════
# TESTS : search_coins
# ══════════════════════════════════════════════════════════════════════

class TestSearchCoins:
    """Tests pour la méthode search_coins"""
    
    @pytest.mark.asyncio
    async def test_search_coins_should_return_cached_results(
        self, service, mock_cache
    ):
        """
        GIVEN des résultats de recherche en cache
        WHEN search_coins est appelé
        THEN les résultats du cache sont retournés
        """
        # Arrange
        query = "bitcoin"
        cached_results = [
            {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"}
        ]
        mock_cache.get.return_value = cached_results
        
        # Act
        result = await service.search_coins(query)
        
        # Assert
        assert result == cached_results
        mock_cache.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_coins_should_limit_results_to_6(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne plus de 6 résultats
        WHEN search_coins est appelé
        THEN seulement 6 résultats sont retournés
        """
        # Arrange
        query = "coin"
        api_response = {
            "coins": [
                {"id": f"coin{i}", "name": f"Coin {i}", "symbol": f"C{i}"}
                for i in range(10)
            ]
        }
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=api_response)
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.search_coins(query)
        
        # Assert
        assert len(result) == 6
    
    @pytest.mark.asyncio
    async def test_search_coins_should_return_empty_list_on_error(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne une erreur
        WHEN search_coins est appelé
        THEN une liste vide est retournée (pas d'exception)
        """
        # Arrange
        query = "bitcoin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.search_coins(query)
        
        # Assert
        assert result == []
    
    @pytest.mark.asyncio
    async def test_search_coins_should_normalize_query_for_cache(
        self, service, mock_cache
    ):
        """
        GIVEN une requête avec majuscules et espaces
        WHEN search_coins est appelé
        THEN la requête est normalisée (lowercase, trim) pour le cache
        """
        # Arrange
        query = "  Bitcoin  "
        expected_cache_key = "search:bitcoin"
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value={"coins": []})
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            await service.search_coins(query)
        
        # Assert
        mock_cache.get.assert_called_with(expected_cache_key)


# ══════════════════════════════════════════════════════════════════════
# TESTS : get_history
# ══════════════════════════════════════════════════════════════════════

class TestGetHistory:
    """Tests pour la méthode get_history"""
    
    @pytest.mark.asyncio
    async def test_get_history_should_return_cached_data(
        self, service, mock_cache
    ):
        """
        GIVEN des données d'historique en cache
        WHEN get_history est appelé
        THEN les données du cache sont retournées
        """
        # Arrange
        coin_id = "bitcoin"
        days = 7
        cached_data = [
            {"date": "01/01", "price": 50000},
            {"date": "02/01", "price": 51000}
        ]
        mock_cache.get.return_value = cached_data
        
        # Act
        result = await service.get_history(coin_id, days)
        
        # Assert
        assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_get_history_should_format_data_for_recharts(
        self, service, mock_cache
    ):
        """
        GIVEN des données brutes de l'API
        WHEN get_history est appelé
        THEN les données sont formatées pour Recharts
        """
        # Arrange
        coin_id = "bitcoin"
        days = 7
        api_response = {
            "prices": [
                [1640995200000, 50000.123456],  # Timestamp en ms
                [1641081600000, 51000.987654]
            ]
        }
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=api_response)
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_history(coin_id, days)
        
        # Assert
        assert len(result) == 2
        assert "date" in result[0]
        assert "price" in result[0]
        assert isinstance(result[0]["price"], (int, float))
    
    @pytest.mark.asyncio
    async def test_get_history_should_return_empty_list_on_error(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne une erreur
        WHEN get_history est appelé
        THEN une liste vide est retournée
        """
        # Arrange
        coin_id = "bitcoin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_history(coin_id)
        
        # Assert
        assert result == []


# ══════════════════════════════════════════════════════════════════════
# TESTS : get_detail
# ══════════════════════════════════════════════════════════════════════

class TestGetDetail:
    """Tests pour la méthode get_detail"""
    
    @pytest.mark.asyncio
    async def test_get_detail_should_return_cached_data(
        self, service, mock_cache
    ):
        """
        GIVEN des détails en cache
        WHEN get_detail est appelé
        THEN les données du cache sont retournées
        """
        # Arrange
        coin_id = "bitcoin"
        cached_data = {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "market": {"price_usd": 50000}
        }
        mock_cache.get.return_value = cached_data
        
        # Act
        result = await service.get_detail(coin_id)
        
        # Assert
        assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_get_detail_should_extract_and_normalize_data(
        self, service, mock_cache
    ):
        """
        GIVEN des données brutes de l'API
        WHEN get_detail est appelé
        THEN les données sont extraites et normalisées
        """
        # Arrange
        coin_id = "bitcoin"
        api_response = {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "btc",
            "description": {"en": "Bitcoin is a cryptocurrency" * 50},  # Long description
            "image": {"large": "https://example.com/bitcoin.png"},
            "links": {
                "homepage": ["https://bitcoin.org"],
                "twitter_screen_name": "bitcoin",
                "subreddit_url": "https://reddit.com/r/bitcoin"
            },
            "market_data": {
                "current_price": {"usd": 50000},
                "market_cap": {"usd": 1000000000},
                "total_volume": {"usd": 50000000},
                "price_change_percentage_24h": 2.5,
                "ath": {"usd": 69000},
                "circulating_supply": 19000000
            },
            "sentiment_votes_up_percentage": 75.5
        }
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=api_response)
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_detail(coin_id)
        
        # Assert
        assert result["id"] == "bitcoin"
        assert result["symbol"] == "BTC"  # Uppercase
        assert len(result["description"]) <= 600  # Truncated
        assert "market" in result
        assert result["market"]["price_usd"] == 50000
    
    @pytest.mark.asyncio
    async def test_get_detail_should_return_empty_dict_on_error(
        self, service, mock_cache
    ):
        """
        GIVEN l'API retourne une erreur
        WHEN get_detail est appelé
        THEN un dictionnaire vide est retourné
        """
        # Arrange
        coin_id = "invalid-coin"
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_detail(coin_id)
        
        # Assert
        assert result == {}
    
    @pytest.mark.asyncio
    async def test_get_detail_should_handle_missing_fields_gracefully(
        self, service, mock_cache
    ):
        """
        GIVEN des données API incomplètes
        WHEN get_detail est appelé
        THEN les champs manquants sont gérés sans erreur
        """
        # Arrange
        coin_id = "bitcoin"
        api_response = {
            "id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "btc",
            # Champs manquants intentionnellement
        }
        
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = Mock(return_value=api_response)
            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            # Act
            result = await service.get_detail(coin_id)
        
        # Assert
        assert result["id"] == "bitcoin"
        assert "market" in result
        # Les valeurs manquantes doivent être None ou des valeurs par défaut

 


# ══════════════════════════════════════════════════════════════════════
# TESTS ADDITIONNELS : Couverture complète des branches stale data
# ══════════════════════════════════════════════════════════════════════

class TestStaleDataFallback:
    """Tests pour la gestion des données périmées (stale data) en fallback"""
    
    @pytest.mark.asyncio
    async def test_get_prices_should_return_stale_on_non_200_with_stale_data(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne une erreur 500 et des données stale existent
        WHEN get_prices est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = {"bitcoin": {"usd": 40000}}
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_prices("bitcoin")
        
        # Assert
        assert result == stale_data
        mock_cache.get_stale.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_prices_should_return_stale_on_timeout_with_stale_data(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API timeout et des données stale existent
        WHEN get_prices est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = {"bitcoin": {"usd": 40000}}
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_prices("bitcoin")
        
        # Assert
        assert result == stale_data
        mock_cache.get_stale.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_coins_should_return_stale_on_429(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne 429 et des données stale existent
        WHEN search_coins est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 429
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.search_coins("bitcoin")
        
        # Assert
        assert result == stale_data
        mock_cache.get_stale.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_coins_should_return_stale_on_non_200(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne une erreur et des données stale existent
        WHEN search_coins est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.search_coins("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_search_coins_should_return_stale_on_timeout(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API timeout et des données stale existent
        WHEN search_coins est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"id": "bitcoin", "name": "Bitcoin", "symbol": "btc"}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.search_coins("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_history_should_return_stale_on_429(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne 429 et des données stale existent
        WHEN get_history est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"date": "01/01", "price": 40000}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 429
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_history("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_history_should_return_stale_on_non_200(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne une erreur et des données stale existent
        WHEN get_history est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"date": "01/01", "price": 40000}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_history("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_history_should_return_stale_on_timeout(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API timeout et des données stale existent
        WHEN get_history est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = [{"date": "01/01", "price": 40000}]
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_history("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_detail_should_return_stale_on_429(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne 429 et des données stale existent
        WHEN get_detail est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = {"id": "bitcoin", "name": "Bitcoin"}
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 429
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_detail("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_detail_should_return_stale_on_non_200(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API retourne une erreur et des données stale existent
        WHEN get_detail est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = {"id": "bitcoin", "name": "Bitcoin"}
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_detail("bitcoin")
        
        # Assert
        assert result == stale_data
    
    @pytest.mark.asyncio
    async def test_get_detail_should_return_stale_on_timeout(
        self, mock_settings, mock_cache, mock_httpx_client
    ):
        """
        GIVEN l'API timeout et des données stale existent
        WHEN get_detail est appelé
        THEN les données stale sont retournées
        """
        # Arrange
        mock_client, mock_response = mock_httpx_client
        service = CoinGeckoService()
        stale_data = {"id": "bitcoin", "name": "Bitcoin"}
        mock_cache.get.return_value = None
        mock_cache.get_stale.return_value = stale_data
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            # Act
            result = await service.get_detail("bitcoin")
        
        # Assert
        assert result == stale_data

 
