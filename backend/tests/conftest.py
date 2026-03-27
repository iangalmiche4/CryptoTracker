"""
conftest.py — Fixtures globales pour tous les tests

Ce fichier contient les fixtures partagées entre tous les tests.
Les fixtures définies ici sont automatiquement disponibles dans tous les tests.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models import User, UserCoin, UserAlert, AlertType


# ══════════════════════════════════════════════════════════════════════
# FIXTURES DE BASE DE DONNÉES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def db_engine():
    """
    Crée un moteur SQLite en mémoire pour les tests
    
    Scope: function - Une nouvelle base pour chaque test
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Crée une session de base de données pour les tests
    
    Scope: function - Une nouvelle session pour chaque test
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def mock_db_session():
    """
    Crée une session DB mockée pour les tests unitaires
    
    Utilisé pour les tests qui ne nécessitent pas de vraie DB
    """
    session = MagicMock()
    return session


# ══════════════════════════════════════════════════════════════════════
# FIXTURES UTILISATEUR
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_user():
    """
    Crée un utilisateur mock pour les tests
    """
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqKqKqKq"
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def test_user(db_session):
    """
    Crée un utilisateur réel en base de données pour les tests d'intégration
    """
    from core.security import hash_password
    
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("TestPassword123!")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def multiple_users(db_session):
    """
    Crée plusieurs utilisateurs pour les tests
    """
    from core.security import hash_password
    
    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            password_hash=hash_password(f"Password{i}123!")
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    
    return users


# ══════════════════════════════════════════════════════════════════════
# FIXTURES COINS
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_user_coin():
    """
    Crée un coin suivi mock pour les tests
    """
    coin = Mock(spec=UserCoin)
    coin.id = 1
    coin.user_id = 1
    coin.coin_id = "bitcoin"
    coin.position = 0
    coin.created_at = datetime.now(timezone.utc)
    return coin


@pytest.fixture
def test_user_coins(db_session, test_user):
    """
    Crée plusieurs coins suivis pour un utilisateur
    """
    coins_data = [
        {"coin_id": "bitcoin", "position": 0},
        {"coin_id": "ethereum", "position": 1},
        {"coin_id": "cardano", "position": 2},
    ]
    
    coins = []
    for data in coins_data:
        coin = UserCoin(
            user_id=test_user.id,
            coin_id=data["coin_id"],
            position=data["position"]
        )
        db_session.add(coin)
        coins.append(coin)
    
    db_session.commit()
    for coin in coins:
        db_session.refresh(coin)
    
    return coins


# ══════════════════════════════════════════════════════════════════════
# FIXTURES ALERTES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_user_alert():
    """
    Crée une alerte mock pour les tests
    """
    alert = Mock(spec=UserAlert)
    alert.id = 1
    alert.user_id = 1
    alert.coin_id = "bitcoin"
    alert.type = AlertType.HIGH
    alert.threshold = 60000.0
    alert.created_at = datetime.now(timezone.utc)
    return alert


@pytest.fixture
def test_user_alerts(db_session, test_user):
    """
    Crée plusieurs alertes pour un utilisateur
    """
    alerts_data = [
        {"coin_id": "bitcoin", "type": AlertType.HIGH, "threshold": 70000.0},
        {"coin_id": "bitcoin", "type": AlertType.LOW, "threshold": 40000.0},
        {"coin_id": "ethereum", "type": AlertType.HIGH, "threshold": 5000.0},
    ]
    
    alerts = []
    for data in alerts_data:
        alert = UserAlert(
            user_id=test_user.id,
            coin_id=data["coin_id"],
            type=data["type"],
            threshold=data["threshold"]
        )
        db_session.add(alert)
        alerts.append(alert)
    
    db_session.commit()
    for alert in alerts:
        db_session.refresh(alert)
    
    return alerts


# ══════════════════════════════════════════════════════════════════════
# FIXTURES CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_settings():
    """
    Crée des settings mockés pour les tests
    """
    from unittest.mock import patch
    
    with patch('core.security.settings') as mock:
        mock.secret_key = "test-secret-key-for-testing-only"
        mock.algorithm = "HS256"
        mock.access_token_expire_minutes = 30
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
    """
    Crée un cache mocké pour les tests
    """
    from unittest.mock import patch
    
    with patch('services.coingecko_service.cache') as mock:
        mock.get = Mock(return_value=None)
        mock.set = Mock()
        mock.get_stale = Mock(return_value=None)
        yield mock


# ══════════════════════════════════════════════════════════════════════
# FIXTURES DONNÉES DE TEST
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_coingecko_prices():
    """
    Données de prix CoinGecko pour les tests
    """
    return {
        "bitcoin": {
            "usd": 50000,
            "usd_24h_change": 2.5,
            "usd_market_cap": 1000000000,
            "usd_24h_vol": 50000000
        },
        "ethereum": {
            "usd": 3000,
            "usd_24h_change": 1.8,
            "usd_market_cap": 350000000,
            "usd_24h_vol": 20000000
        }
    }


@pytest.fixture
def sample_coingecko_search():
    """
    Résultats de recherche CoinGecko pour les tests
    """
    return {
        "coins": [
            {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC"},
            {"id": "ethereum", "name": "Ethereum", "symbol": "ETH"},
            {"id": "cardano", "name": "Cardano", "symbol": "ADA"},
        ]
    }


@pytest.fixture
def sample_coingecko_history():
    """
    Historique de prix CoinGecko pour les tests
    """
    return {
        "prices": [
            [1640995200000, 50000.123456],
            [1641081600000, 51000.987654],
            [1641168000000, 49500.456789],
        ]
    }


@pytest.fixture
def sample_coingecko_detail():
    """
    Détails d'un coin CoinGecko pour les tests
    """
    return {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "btc",
        "description": {"en": "Bitcoin is a cryptocurrency"},
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
            "price_change_percentage_7d": 5.2,
            "price_change_percentage_30d": 10.8,
            "ath": {"usd": 69000},
            "ath_change_percentage": {"usd": -27.5},
            "circulating_supply": 19000000,
            "total_supply": 21000000,
            "max_supply": 21000000
        },
        "sentiment_votes_up_percentage": 75.5
    }


# ══════════════════════════════════════════════════════════════════════
# HOOKS PYTEST
# ══════════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """
    Configuration globale de pytest
    """
    config.addinivalue_line(
        "markers", "unit: Tests unitaires avec isolation complète"
    )
    config.addinivalue_line(
        "markers", "integration: Tests d'intégration avec dépendances"
    )
    config.addinivalue_line(
        "markers", "slow: Tests lents (> 1 seconde)"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modifier les items de test collectés
    
    Ajoute automatiquement le marker 'unit' aux tests dans tests/unit/
    """
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

 
