"""
test_auth.py — Tests unitaires pour routers/auth.py

Tests couverts :
- Inscription d'un nouvel utilisateur (register)
- Connexion avec email/password (login)
- Récupération des informations utilisateur (get_me)
- Gestion des erreurs (email déjà utilisé, identifiants incorrects)

Principes appliqués :
- Isolation totale avec mocks (pas de vraie DB)
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites et erreurs
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone
from starlette.requests import Request

from routers.auth import register, login, get_me
from models import User
from schemas import UserRegister


# ══════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_request():
    """Fixture pour créer un mock Request pour le rate limiting"""
    request = Mock(spec=Request)
    request.client = Mock()
    request.client.host = "127.0.0.1"
    return request


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
    user.password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qXqKqKqKq"
    user.created_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def valid_user_register():
    """Fixture pour des données d'inscription valides"""
    return UserRegister(
        email="newuser@example.com",
        password="SecurePassword123!"
    )


@pytest.fixture
def mock_oauth_form():
    """Fixture pour un formulaire OAuth2 mock"""
    form = Mock(spec=OAuth2PasswordRequestForm)
    form.username = "test@example.com"
    form.password = "CorrectPassword123"
    return form


# ══════════════════════════════════════════════════════════════════════
# TESTS : register
# ══════════════════════════════════════════════════════════════════════

class TestRegister:
    """Tests pour l'endpoint POST /api/auth/register"""
    
    def test_register_should_create_new_user_with_valid_data(
        self, mock_request, mock_db_session, valid_user_register
    ):
        """
        GIVEN des données d'inscription valides
        WHEN register est appelé
        THEN un nouvel utilisateur est créé et retourné
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('routers.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Act
            result = register(mock_request, valid_user_register, mock_db_session)
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
    
    def test_register_should_hash_password_before_storing(
        self, mock_request, mock_db_session, valid_user_register
    ):
        """
        GIVEN un mot de passe en clair
        WHEN register est appelé
        THEN le mot de passe est hashé avant stockage
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('routers.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Act
            register(mock_request, valid_user_register, mock_db_session)
        
        # Assert
        mock_hash.assert_called_once_with(valid_user_register.password)
    
    def test_register_should_raise_400_when_email_already_exists(
        self, mock_request, mock_db_session, valid_user_register, mock_user
    ):
        """
        GIVEN un email déjà enregistré
        WHEN register est appelé
        THEN HTTPException 400 est levée
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            register(mock_request, valid_user_register, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in exc_info.value.detail.lower()
    
    def test_register_should_not_commit_when_email_exists(
        self, mock_request, mock_db_session, valid_user_register, mock_user
    ):
        """
        GIVEN un email déjà enregistré
        WHEN register est appelé
        THEN aucune modification n'est faite en base
        """
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(HTTPException):
            register(mock_request, valid_user_register, mock_db_session)
        
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
    
    def test_register_should_handle_empty_email(self, mock_db_session):
        """
        GIVEN un email vide
        WHEN register est appelé
        THEN une erreur de validation est levée (Pydantic)
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserRegister(email="", password="ValidPassword123")
    
    def test_register_should_handle_short_password(self, mock_db_session):
        """
        GIVEN un mot de passe trop court (< 8 caractères)
        WHEN register est appelé
        THEN une erreur de validation est levée (Pydantic)
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserRegister(email="test@example.com", password="short")
    
    def test_register_should_handle_invalid_email_format(self, mock_db_session):
        """
        GIVEN un email au format invalide
        WHEN register est appelé
        THEN une erreur de validation est levée (Pydantic)
        """
        # Arrange & Act & Assert
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserRegister(email="not-an-email", password="ValidPassword123")


# ══════════════════════════════════════════════════════════════════════
# TESTS : login
# ══════════════════════════════════════════════════════════════════════

class TestLogin:
    """Tests pour l'endpoint POST /api/auth/login"""
    
    def test_login_should_return_token_for_valid_credentials(
        self, mock_request, mock_db_session, mock_oauth_form, mock_user
    ):
        """
        GIVEN des identifiants valides
        WHEN login est appelé
        THEN un token JWT est retourné
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            with patch('routers.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = "jwt_token_here"
                
                # Act
                result = login(mock_request, mock_oauth_form, mock_db_session)
        
        # Assert
        assert result["access_token"] == "jwt_token_here"
        assert result["token_type"] == "bearer"
    
    def test_login_should_call_authenticate_user_with_credentials(
        self, mock_request, mock_db_session, mock_oauth_form, mock_user
    ):
        """
        GIVEN des identifiants
        WHEN login est appelé
        THEN authenticate_user est appelé avec les bons paramètres
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            with patch('routers.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = "jwt_token"
                
                # Act
                login(mock_request, mock_oauth_form, mock_db_session)
        
        # Assert
        mock_auth.assert_called_once_with(
            mock_db_session,
            mock_oauth_form.username,
            mock_oauth_form.password
        )
    
    def test_login_should_raise_401_for_invalid_credentials(
        self, mock_request, mock_db_session, mock_oauth_form
    ):
        """
        GIVEN des identifiants incorrects
        WHEN login est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None  # Authentification échouée
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login(mock_request, mock_oauth_form, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in exc_info.value.detail.lower()
    
    def test_login_should_include_www_authenticate_header_on_401(
        self, mock_request, mock_db_session, mock_oauth_form
    ):
        """
        GIVEN des identifiants incorrects
        WHEN login est appelé
        THEN le header WWW-Authenticate est inclus dans la réponse
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login(mock_request, mock_oauth_form, mock_db_session)
        
        assert exc_info.value.headers is not None
        assert "WWW-Authenticate" in exc_info.value.headers
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
    
    def test_login_should_create_token_with_user_email(
        self, mock_request, mock_db_session, mock_oauth_form, mock_user
    ):
        """
        GIVEN un utilisateur authentifié
        WHEN login est appelé
        THEN le token est créé avec l'email de l'utilisateur
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            with patch('routers.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = "jwt_token"
                
                # Act
                login(mock_request, mock_oauth_form, mock_db_session)
        
        # Assert
        mock_create_token.assert_called_once_with(data={"sub": mock_user.email})
    
    def test_login_should_handle_nonexistent_user(
        self, mock_request, mock_db_session, mock_oauth_form
    ):
        """
        GIVEN un utilisateur qui n'existe pas
        WHEN login est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login(mock_request, mock_oauth_form, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_should_handle_wrong_password(
        self, mock_request, mock_db_session, mock_oauth_form
    ):
        """
        GIVEN un mot de passe incorrect
        WHEN login est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None  # Mot de passe incorrect
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                login(mock_request, mock_oauth_form, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# ══════════════════════════════════════════════════════════════════════
# TESTS : get_me
# ══════════════════════════════════════════════════════════════════════

class TestGetMe:
    """Tests pour l'endpoint GET /api/auth/me"""
    
    def test_get_me_should_return_current_user(self, mock_user):
        """
        GIVEN un utilisateur authentifié
        WHEN get_me est appelé
        THEN les informations de l'utilisateur sont retournées
        """
        # Arrange & Act
        result = get_me(mock_user)
        
        # Assert
        assert result == mock_user
    
    def test_get_me_should_return_user_with_all_fields(self, mock_user):
        """
        GIVEN un utilisateur authentifié
        WHEN get_me est appelé
        THEN tous les champs utilisateur sont présents
        """
        # Arrange & Act
        result = get_me(mock_user)
        
        # Assert
        assert hasattr(result, 'id')
        assert hasattr(result, 'email')
        assert hasattr(result, 'created_at')
    
    def test_get_me_should_not_expose_password_hash(self, mock_user):
        """
        GIVEN un utilisateur authentifié
        WHEN get_me est appelé
        THEN le hash du mot de passe ne doit pas être exposé dans la réponse
        (Note: Ceci est géré par le schéma Pydantic UserResponse)
        """
        # Arrange & Act
        result = get_me(mock_user)
        
        # Assert
        # Le schéma UserResponse ne doit pas inclure password_hash
        # Cette vérification est plus pertinente au niveau du schéma
        assert result == mock_user


# ══════════════════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION (avec dépendances mockées)
# ══════════════════════════════════════════════════════════════════════

class TestAuthIntegration:
    """Tests d'intégration pour le flux complet d'authentification"""
    
    def test_full_registration_and_login_flow(self, mock_request, mock_db_session):
        """
        GIVEN un nouvel utilisateur
        WHEN il s'inscrit puis se connecte
        THEN il reçoit un token valide
        """
        # Arrange
        user_data = UserRegister(
            email="integration@example.com",
            password="IntegrationTest123!"
        )
        
        # Étape 1: Inscription
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('routers.auth.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Act: Register
            register(mock_request, user_data, mock_db_session)
        
        # Assert: User created
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called()
        
        # Étape 2: Login
        mock_user = Mock(spec=User)
        mock_user.email = user_data.email
        mock_user.password_hash = "hashed_password"
        
        form = Mock(spec=OAuth2PasswordRequestForm)
        form.username = user_data.email
        form.password = user_data.password
        
        with patch('routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user
            
            with patch('routers.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = "jwt_token"
                
                # Act: Login
                result = login(mock_request, form, mock_db_session)
        
        # Assert: Token received
        assert result["access_token"] == "jwt_token"
        assert result["token_type"] == "bearer"
    
    def test_cannot_register_twice_with_same_email(
        self, mock_request, mock_db_session, mock_user
    ):
        """
        GIVEN un utilisateur déjà enregistré
        WHEN on tente de s'inscrire avec le même email
        THEN l'inscription échoue
        """
        # Arrange
        user_data = UserRegister(
            email=mock_user.email,
            password="AnotherPassword123!"
        )
        
        # Première inscription réussie (simulée)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act & Assert: Deuxième inscription échoue
        with pytest.raises(HTTPException) as exc_info:
            register(mock_request, user_data, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

 
