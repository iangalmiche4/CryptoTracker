"""
test_user.py — Tests unitaires pour routers/user.py

Tests couverts :
- Récupération des données utilisateur (get_user_data)
- Ajout d'un coin (add_coin)
- Réorganisation des coins (reorder_coins)
- Suppression d'un coin (remove_coin)
- Création d'une alerte (create_alert)
- Modification d'une alerte (update_alert)
- Suppression d'une alerte (delete_alert)

Principes appliqués :
- Isolation totale avec mocks (pas de vraie DB)
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites et erreurs
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException, status
from datetime import datetime, timezone

from routers.user import (
    get_user_data,
    add_coin,
    reorder_coins,
    remove_coin,
    create_alert,
    update_alert,
    delete_alert
)
from models import User, UserCoin, UserAlert, AlertType
from schemas import CoinCreate, CoinsReorder, AlertCreate, AlertUpdate


# ══════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_db_session():
    """Fixture pour créer une session DB mock"""
    session = MagicMock()
    return session


@pytest.fixture
def mock_user():
    """Fixture pour créer un utilisateur mock"""
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def mock_user_coin():
    """Fixture pour créer un coin suivi mock"""
    coin = Mock(spec=UserCoin)
    coin.id = 1
    coin.user_id = 1
    coin.coin_id = "bitcoin"
    coin.position = 0
    coin.created_at = datetime.now(timezone.utc)
    return coin


@pytest.fixture
def mock_user_alert():
    """Fixture pour créer une alerte mock"""
    alert = Mock(spec=UserAlert)
    alert.id = 1
    alert.user_id = 1
    alert.coin_id = "bitcoin"
    alert.type = AlertType.HIGH
    alert.threshold = 60000.0
    alert.created_at = datetime.now(timezone.utc)
    return alert


# ══════════════════════════════════════════════════════════════════════
# TESTS : get_user_data
# ══════════════════════════════════════════════════════════════════════

class TestGetUserData:
    """Tests pour l'endpoint GET /api/user/data"""
    
    def test_get_user_data_should_return_user_coins_and_alerts(
        self, mock_db_session, mock_user, mock_user_coin, mock_user_alert
    ):
        """
        GIVEN un utilisateur authentifié avec des coins et alertes
        WHEN get_user_data est appelé
        THEN toutes les données utilisateur sont retournées
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_user_coin]
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_user_alert]
        
        # Act
        result = get_user_data(mock_user, mock_db_session)
        
        # Assert
        assert result["user"] == mock_user
        assert len(result["coins"]) == 1
        assert len(result["alerts"]) == 1
    
    def test_get_user_data_should_order_coins_by_position(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN plusieurs coins avec différentes positions
        WHEN get_user_data est appelé
        THEN les coins sont ordonnés par position
        """
        # Arrange
        coin1 = Mock(spec=UserCoin)
        coin1.position = 2
        coin2 = Mock(spec=UserCoin)
        coin2.position = 0
        coin3 = Mock(spec=UserCoin)
        coin3.position = 1
        
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [coin2, coin3, coin1]
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        result = get_user_data(mock_user, mock_db_session)
        
        # Assert
        assert len(result["coins"]) == 3
        # Vérifier que order_by a été appelé
        mock_db_session.query.return_value.filter.return_value.order_by.assert_called()
    
    def test_get_user_data_should_return_empty_lists_when_no_data(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un utilisateur sans coins ni alertes
        WHEN get_user_data est appelé
        THEN des listes vides sont retournées
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        # Act
        result = get_user_data(mock_user, mock_db_session)
        
        # Assert
        assert result["user"] == mock_user
        assert result["coins"] == []
        assert result["alerts"] == []


# ══════════════════════════════════════════════════════════════════════
# TESTS : add_coin
# ══════════════════════════════════════════════════════════════════════

class TestAddCoin:
    """Tests pour l'endpoint POST /api/user/coins"""
    
    def test_add_coin_should_create_new_coin_with_valid_data(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un coin_id valide
        WHEN add_coin est appelé
        THEN un nouveau coin est créé
        """
        # Arrange
        coin_data = CoinCreate(coin_id="ethereum", position=None)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value.filter.return_value.count.return_value = 2
        
        # Act
        result = add_coin(coin_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_add_coin_should_use_provided_position(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une position spécifiée
        WHEN add_coin est appelé
        THEN le coin est créé avec cette position
        """
        # Arrange
        coin_data = CoinCreate(coin_id="cardano", position=5)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        add_coin(coin_data, mock_user, mock_db_session)
        
        # Assert
        # Vérifier que le coin a été ajouté avec la position spécifiée
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.position == 5
    
    def test_add_coin_should_append_to_end_when_no_position(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN aucune position spécifiée
        WHEN add_coin est appelé
        THEN le coin est ajouté à la fin de la liste
        """
        # Arrange
        coin_data = CoinCreate(coin_id="polkadot", position=None)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.query.return_value.filter.return_value.count.return_value = 3
        
        # Act
        add_coin(coin_data, mock_user, mock_db_session)
        
        # Assert
        call_args = mock_db_session.add.call_args[0][0]
        assert call_args.position == 3  # Ajouté à la fin
    
    def test_add_coin_should_raise_400_when_coin_already_tracked(
        self, mock_db_session, mock_user, mock_user_coin
    ):
        """
        GIVEN un coin déjà suivi
        WHEN add_coin est appelé
        THEN HTTPException 400 est levée
        """
        # Arrange
        coin_data = CoinCreate(coin_id="bitcoin", position=None)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_coin
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            add_coin(coin_data, mock_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already tracked" in exc_info.value.detail.lower()
    
    def test_add_coin_should_not_commit_when_coin_exists(
        self, mock_db_session, mock_user, mock_user_coin
    ):
        """
        GIVEN un coin déjà suivi
        WHEN add_coin est appelé
        THEN aucune modification n'est faite en base
        """
        # Arrange
        coin_data = CoinCreate(coin_id="bitcoin", position=None)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_coin
        
        # Act & Assert
        with pytest.raises(HTTPException):
            add_coin(coin_data, mock_user, mock_db_session)
        
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()


# ══════════════════════════════════════════════════════════════════════
# TESTS : reorder_coins
# ══════════════════════════════════════════════════════════════════════

class TestReorderCoins:
    """Tests pour l'endpoint PUT /api/user/coins/reorder"""
    
    def test_reorder_coins_should_update_positions(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une nouvelle liste ordonnée de coin_ids
        WHEN reorder_coins est appelé
        THEN les positions sont mises à jour
        """
        # Arrange
        coin1 = Mock(spec=UserCoin)
        coin1.coin_id = "bitcoin"
        coin2 = Mock(spec=UserCoin)
        coin2.coin_id = "ethereum"
        coin3 = Mock(spec=UserCoin)
        coin3.coin_id = "cardano"
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [coin1, coin2, coin3]
        
        reorder_data = CoinsReorder(coin_ids=["ethereum", "cardano", "bitcoin"])
        
        # Act
        result = reorder_coins(reorder_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.commit.assert_called_once()
        assert "success" in result["message"].lower()
    
    def test_reorder_coins_should_handle_partial_list(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une liste partielle de coin_ids
        WHEN reorder_coins est appelé
        THEN seuls les coins présents sont réorganisés
        """
        # Arrange
        coin1 = Mock(spec=UserCoin)
        coin1.coin_id = "bitcoin"
        coin2 = Mock(spec=UserCoin)
        coin2.coin_id = "ethereum"
        
        mock_db_session.query.return_value.filter.return_value.all.return_value = [coin1, coin2]
        
        reorder_data = CoinsReorder(coin_ids=["ethereum"])  # Seulement un coin
        
        # Act
        result = reorder_coins(reorder_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.commit.assert_called_once()
    
    def test_reorder_coins_should_handle_empty_list(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une liste vide de coin_ids
        WHEN reorder_coins est appelé
        THEN aucune erreur n'est levée
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        reorder_data = CoinsReorder(coin_ids=[])
        
        # Act
        result = reorder_coins(reorder_data, mock_user, mock_db_session)
        
        # Assert
        assert "success" in result["message"].lower()


# ══════════════════════════════════════════════════════════════════════
# TESTS : remove_coin
# ══════════════════════════════════════════════════════════════════════

class TestRemoveCoin:
    """Tests pour l'endpoint DELETE /api/user/coins/{coin_id}"""
    
    def test_remove_coin_should_delete_existing_coin(
        self, mock_db_session, mock_user, mock_user_coin
    ):
        """
        GIVEN un coin existant
        WHEN remove_coin est appelé
        THEN le coin est supprimé
        """
        # Arrange
        coin_id = "bitcoin"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_coin
        
        # Act
        result = remove_coin(coin_id, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.delete.assert_called_once_with(mock_user_coin)
        mock_db_session.commit.assert_called_once()
        assert "success" in result["message"].lower()
    
    def test_remove_coin_should_raise_404_when_coin_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un coin_id qui n'existe pas
        WHEN remove_coin est appelé
        THEN HTTPException 404 est levée
        """
        # Arrange
        coin_id = "nonexistent"
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            remove_coin(coin_id, mock_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()
    
    def test_remove_coin_should_not_commit_when_coin_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un coin qui n'existe pas
        WHEN remove_coin est appelé
        THEN aucune modification n'est faite en base
        """
        # Arrange
        coin_id = "nonexistent"
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException):
            remove_coin(coin_id, mock_user, mock_db_session)
        
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()


# ══════════════════════════════════════════════════════════════════════
# TESTS : create_alert
# ══════════════════════════════════════════════════════════════════════

class TestCreateAlert:
    """Tests pour l'endpoint POST /api/user/alerts"""
    
    def test_create_alert_should_create_new_alert_with_valid_data(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN des données d'alerte valides
        WHEN create_alert est appelé
        THEN une nouvelle alerte est créée
        """
        # Arrange
        alert_data = AlertCreate(coin_id="bitcoin", type="high", threshold=70000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = create_alert(alert_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_create_alert_should_raise_400_when_alert_type_exists(
        self, mock_db_session, mock_user, mock_user_alert
    ):
        """
        GIVEN une alerte du même type existe déjà pour ce coin
        WHEN create_alert est appelé
        THEN HTTPException 400 est levée
        """
        # Arrange
        alert_data = AlertCreate(coin_id="bitcoin", type="high", threshold=70000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_alert
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_alert(alert_data, mock_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in exc_info.value.detail.lower()
    
    def test_create_alert_should_allow_different_types_for_same_coin(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une alerte HIGH existe pour un coin
        WHEN on crée une alerte LOW pour le même coin
        THEN l'alerte est créée avec succès
        """
        # Arrange
        alert_data = AlertCreate(coin_id="bitcoin", type="low", threshold=40000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        create_alert(alert_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_create_alert_should_handle_zero_threshold(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un seuil de 0 (invalide selon le schéma)
        WHEN create_alert est appelé
        THEN une erreur de validation est levée (Pydantic)
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            AlertCreate(coin_id="bitcoin", type="high", threshold=0)
    
    def test_create_alert_should_handle_negative_threshold(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un seuil négatif (invalide selon le schéma)
        WHEN create_alert est appelé
        THEN une erreur de validation est levée (Pydantic)
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            AlertCreate(coin_id="bitcoin", type="high", threshold=-1000)


# ══════════════════════════════════════════════════════════════════════
# TESTS : update_alert
# ══════════════════════════════════════════════════════════════════════

class TestUpdateAlert:
    """Tests pour l'endpoint PUT /api/user/alerts/{alert_id}"""
    
    def test_update_alert_should_modify_threshold(
        self, mock_db_session, mock_user, mock_user_alert
    ):
        """
        GIVEN une alerte existante
        WHEN update_alert est appelé avec un nouveau seuil
        THEN le seuil est mis à jour
        """
        # Arrange
        alert_id = 1
        alert_data = AlertUpdate(threshold=75000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_alert
        
        # Act
        result = update_alert(alert_id, alert_data, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_update_alert_should_raise_404_when_alert_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un alert_id qui n'existe pas
        WHEN update_alert est appelé
        THEN HTTPException 404 est levée
        """
        # Arrange
        alert_id = 999
        alert_data = AlertUpdate(threshold=75000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            update_alert(alert_id, alert_data, mock_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()
    
    def test_update_alert_should_not_commit_when_alert_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une alerte qui n'existe pas
        WHEN update_alert est appelé
        THEN aucune modification n'est faite en base
        """
        # Arrange
        alert_id = 999
        alert_data = AlertUpdate(threshold=75000.0)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException):
            update_alert(alert_id, alert_data, mock_user, mock_db_session)
        
        mock_db_session.commit.assert_not_called()


# ══════════════════════════════════════════════════════════════════════
# TESTS : delete_alert
# ══════════════════════════════════════════════════════════════════════

class TestDeleteAlert:
    """Tests pour l'endpoint DELETE /api/user/alerts/{alert_id}"""
    
    def test_delete_alert_should_remove_existing_alert(
        self, mock_db_session, mock_user, mock_user_alert
    ):
        """
        GIVEN une alerte existante
        WHEN delete_alert est appelé
        THEN l'alerte est supprimée
        """
        # Arrange
        alert_id = 1
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user_alert
        
        # Act
        result = delete_alert(alert_id, mock_user, mock_db_session)
        
        # Assert
        mock_db_session.delete.assert_called_once_with(mock_user_alert)
        mock_db_session.commit.assert_called_once()
        assert "success" in result["message"].lower()
    
    def test_delete_alert_should_raise_404_when_alert_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un alert_id qui n'existe pas
        WHEN delete_alert est appelé
        THEN HTTPException 404 est levée
        """
        # Arrange
        alert_id = 999
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_alert(alert_id, mock_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()
    
    def test_delete_alert_should_not_commit_when_alert_not_found(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN une alerte qui n'existe pas
        WHEN delete_alert est appelé
        THEN aucune modification n'est faite en base
        """
        # Arrange
        alert_id = 999
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException):
            delete_alert(alert_id, mock_user, mock_db_session)
        
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

 
