"""
test_security.py — Tests unitaires pour le module core/security.py

Tests couverts :
- Hachage et vérification des mots de passe (bcrypt)
- Création et décodage des tokens JWT
- Authentification utilisateur
- Récupération de l'utilisateur courant (dépendance FastAPI)

Principes appliqués :
- Isolation totale avec mocks
- Pattern AAA (Arrange-Act-Assert)
- Couverture des cas limites et erreurs
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock, patch
from jose import jwt, JWTError
from fastapi import HTTPException, status

from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    authenticate_user,
    get_current_user,
)
from models import User


# ══════════════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════════════

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
def mock_db_session():
    """Fixture pour créer une session DB mock"""
    session = MagicMock()
    return session


@pytest.fixture
def valid_token_payload():
    """Fixture pour un payload JWT valide"""
    return {"sub": "test@example.com"}


@pytest.fixture
def mock_settings():
    """Fixture pour mocker les settings"""
    with patch('core.security.settings') as mock:
        mock.secret_key = "test-secret-key-for-testing-only"
        mock.algorithm = "HS256"
        mock.access_token_expire_minutes = 30
        yield mock


# ══════════════════════════════════════════════════════════════════════
# TESTS : Hachage de mots de passe
# ══════════════════════════════════════════════════════════════════════

class TestPasswordHashing:
    """Tests pour le hachage et la vérification des mots de passe"""
    
    def test_hash_password_should_return_bcrypt_hash(self):
        """
        GIVEN un mot de passe en clair
        WHEN hash_password est appelé
        THEN un hash bcrypt valide est retourné
        """
        # Arrange
        password = "SecurePassword123!"
        
        # Act
        hashed = hash_password(password)
        
        # Assert
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # Bcrypt prefix
        assert len(hashed) == 60  # Bcrypt hash length
        assert hashed != password  # Hash différent du mot de passe
    
    def test_hash_password_should_generate_different_hashes_for_same_password(self):
        """
        GIVEN le même mot de passe hashé deux fois
        WHEN hash_password est appelé
        THEN deux hashes différents sont générés (salt aléatoire)
        """
        # Arrange
        password = "SamePassword123"
        
        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Assert
        assert hash1 != hash2  # Salts différents
    
    def test_verify_password_should_return_true_for_correct_password(self):
        """
        GIVEN un mot de passe et son hash
        WHEN verify_password est appelé avec le bon mot de passe
        THEN True est retourné
        """
        # Arrange
        password = "CorrectPassword123"
        hashed = hash_password(password)
        
        # Act
        result = verify_password(password, hashed)
        
        # Assert
        assert result is True
    
    def test_verify_password_should_return_false_for_incorrect_password(self):
        """
        GIVEN un mot de passe et son hash
        WHEN verify_password est appelé avec un mauvais mot de passe
        THEN False est retourné
        """
        # Arrange
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(correct_password)
        
        # Act
        result = verify_password(wrong_password, hashed)
        
        # Assert
        assert result is False
    
    def test_verify_password_should_handle_empty_password(self):
        """
        GIVEN un hash valide
        WHEN verify_password est appelé avec un mot de passe vide
        THEN False est retourné
        """
        # Arrange
        hashed = hash_password("SomePassword")
        
        # Act
        result = verify_password("", hashed)
        
        # Assert
        assert result is False
    
    def test_verify_password_should_handle_invalid_hash(self):
        """
        GIVEN un hash invalide
        WHEN verify_password est appelé
        THEN une exception est levée ou False est retourné
        """
        # Arrange
        password = "SomePassword"
        invalid_hash = "not-a-valid-bcrypt-hash"
        
        # Act & Assert
        with pytest.raises(ValueError):
            verify_password(password, invalid_hash)


# ══════════════════════════════════════════════════════════════════════
# TESTS : Tokens JWT
# ══════════════════════════════════════════════════════════════════════

class TestJWTTokens:
    """Tests pour la création et le décodage des tokens JWT"""
    
    def test_create_access_token_should_return_valid_jwt(self, mock_settings):
        """
        GIVEN des données utilisateur
        WHEN create_access_token est appelé
        THEN un token JWT valide est retourné
        """
        # Arrange
        data = {"sub": "user@example.com"}
        
        # Act
        token = create_access_token(data)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Vérifier que le token peut être décodé
        decoded = jwt.decode(
            token,
            mock_settings.secret_key,
            algorithms=[mock_settings.algorithm]
        )
        assert decoded["sub"] == "user@example.com"
        assert "exp" in decoded
    
    def test_create_access_token_should_include_expiration(self, mock_settings):
        """
        GIVEN des données utilisateur
        WHEN create_access_token est appelé
        THEN le token contient une date d'expiration
        """
        # Arrange
        data = {"sub": "user@example.com"}
        
        # Act
        token = create_access_token(data)
        decoded = jwt.decode(
            token,
            mock_settings.secret_key,
            algorithms=[mock_settings.algorithm]
        )
        
        # Assert
        assert "exp" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp_time > now  # Expiration dans le futur
    
    def test_create_access_token_should_respect_custom_expiration(self, mock_settings):
        """
        GIVEN une durée d'expiration personnalisée
        WHEN create_access_token est appelé
        THEN le token expire selon la durée spécifiée
        """
        # Arrange
        data = {"sub": "user@example.com"}
        custom_delta = timedelta(minutes=5)
        
        # Act
        token = create_access_token(data, expires_delta=custom_delta)
        decoded = jwt.decode(
            token,
            mock_settings.secret_key,
            algorithms=[mock_settings.algorithm]
        )
        
        # Assert
        exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        expected_exp = now + custom_delta
        
        # Tolérance de 2 secondes pour l'exécution du test
        assert abs((exp_time - expected_exp).total_seconds()) < 2
    
    def test_decode_access_token_should_return_email_for_valid_token(self, mock_settings):
        """
        GIVEN un token JWT valide
        WHEN decode_access_token est appelé
        THEN l'email de l'utilisateur est retourné
        """
        # Arrange
        email = "test@example.com"
        token = create_access_token({"sub": email})
        
        # Act
        result = decode_access_token(token)
        
        # Assert
        assert result == email
    
    def test_decode_access_token_should_return_none_for_invalid_token(self, mock_settings):
        """
        GIVEN un token JWT invalide
        WHEN decode_access_token est appelé
        THEN None est retourné
        """
        # Arrange
        invalid_token = "invalid.jwt.token"
        
        # Act
        result = decode_access_token(invalid_token)
        
        # Assert
        assert result is None
    
    def test_decode_access_token_should_return_none_for_expired_token(self, mock_settings):
        """
        GIVEN un token JWT expiré
        WHEN decode_access_token est appelé
        THEN None est retourné
        """
        # Arrange
        expired_delta = timedelta(minutes=-10)  # Expiré il y a 10 minutes
        token = create_access_token({"sub": "test@example.com"}, expires_delta=expired_delta)
        
        # Act
        result = decode_access_token(token)
        
        # Assert
        assert result is None
    
    def test_decode_access_token_should_return_none_when_sub_missing(self, mock_settings):
        """
        GIVEN un token JWT sans champ 'sub'
        WHEN decode_access_token est appelé
        THEN None est retourné
        """
        # Arrange
        # Créer un token sans 'sub'
        payload = {"user_id": 123, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        token = jwt.encode(payload, mock_settings.secret_key, algorithm=mock_settings.algorithm)
        
        # Act
        result = decode_access_token(token)
        
        # Assert
        assert result is None


# ══════════════════════════════════════════════════════════════════════
# TESTS : Authentification utilisateur
# ══════════════════════════════════════════════════════════════════════

class TestAuthenticateUser:
    """Tests pour la fonction authenticate_user"""
    
    def test_authenticate_user_should_return_user_for_valid_credentials(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN des identifiants valides
        WHEN authenticate_user est appelé
        THEN l'utilisateur est retourné
        """
        # Arrange
        email = "test@example.com"
        password = "CorrectPassword123"
        mock_user.password_hash = hash_password(password)
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act
        result = authenticate_user(mock_db_session, email, password)
        
        # Assert
        assert result == mock_user
        mock_db_session.query.assert_called_once()
    
    def test_authenticate_user_should_return_none_for_nonexistent_user(
        self, mock_db_session
    ):
        """
        GIVEN un email qui n'existe pas
        WHEN authenticate_user est appelé
        THEN None est retourné
        """
        # Arrange
        email = "nonexistent@example.com"
        password = "SomePassword"
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = authenticate_user(mock_db_session, email, password)
        
        # Assert
        assert result is None
    
    def test_authenticate_user_should_return_none_for_wrong_password(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un mot de passe incorrect
        WHEN authenticate_user est appelé
        THEN None est retourné
        """
        # Arrange
        email = "test@example.com"
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        mock_user.password_hash = hash_password(correct_password)
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act
        result = authenticate_user(mock_db_session, email, wrong_password)
        
        # Assert
        assert result is None
    
    def test_authenticate_user_should_handle_empty_password(
        self, mock_db_session, mock_user
    ):
        """
        GIVEN un mot de passe vide
        WHEN authenticate_user est appelé
        THEN None est retourné
        """
        # Arrange
        email = "test@example.com"
        mock_user.password_hash = hash_password("SomePassword")
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act
        result = authenticate_user(mock_db_session, email, "")
        
        # Assert
        assert result is None


# ══════════════════════════════════════════════════════════════════════
# TESTS : Dépendance get_current_user
# ══════════════════════════════════════════════════════════════════════

class TestGetCurrentUser:
    """Tests pour la dépendance FastAPI get_current_user"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_should_return_user_for_valid_token(
        self, mock_db_session, mock_user, mock_settings
    ):
        """
        GIVEN un token JWT valide
        WHEN get_current_user est appelé
        THEN l'utilisateur correspondant est retourné
        """
        # Arrange
        email = "test@example.com"
        token = create_access_token({"sub": email})
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act
        result = await get_current_user(token, mock_db_session)
        
        # Assert
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_user_should_raise_401_for_invalid_token(
        self, mock_db_session, mock_settings
    ):
        """
        GIVEN un token JWT invalide
        WHEN get_current_user est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        invalid_token = "invalid.jwt.token"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(invalid_token, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_should_raise_401_when_user_not_found(
        self, mock_db_session, mock_settings
    ):
        """
        GIVEN un token valide mais l'utilisateur n'existe plus en base
        WHEN get_current_user est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        email = "deleted@example.com"
        token = create_access_token({"sub": email})
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_should_raise_401_for_expired_token(
        self, mock_db_session, mock_settings
    ):
        """
        GIVEN un token JWT expiré
        WHEN get_current_user est appelé
        THEN HTTPException 401 est levée
        """
        # Arrange
        expired_delta = timedelta(minutes=-10)
        token = create_access_token({"sub": "test@example.com"}, expires_delta=expired_delta)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

 
