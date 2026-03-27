"""
test_exceptions.py — Tests unitaires pour core/exceptions.py

Tests couverts :
- Création d'exceptions personnalisées
- Messages d'erreur personnalisés
- Conversion en HTTPException FastAPI
- Codes de statut HTTP appropriés
- Headers HTTP (WWW-Authenticate)

Principes appliqués :
- Isolation totale
- Pattern AAA (Arrange-Act-Assert)
- Couverture complète des exceptions
"""

import pytest
from fastapi import HTTPException, status

from core.exceptions import (
    CryptoTrackerException,
    CoinGeckoException,
    RateLimitException,
    TimeoutException,
    APIException,
    AuthenticationException,
    InvalidCredentialsException,
    TokenExpiredException,
    ValidationException,
    InvalidCoinIdException,
    to_http_exception
)


# ══════════════════════════════════════════════════════════════════════
# TESTS : Exceptions de base
# ══════════════════════════════════════════════════════════════════════

class TestBaseExceptions:
    """Tests pour les exceptions de base"""
    
    def test_crypto_tracker_exception_should_be_base_exception(self):
        """
        GIVEN CryptoTrackerException
        WHEN elle est instanciée
        THEN elle hérite de Exception
        """
        # Act
        exc = CryptoTrackerException("test message")
        
        # Assert
        assert isinstance(exc, Exception)
        assert str(exc) == "test message"
    
    def test_coingecko_exception_should_inherit_from_base(self):
        """
        GIVEN CoinGeckoException
        WHEN elle est instanciée
        THEN elle hérite de CryptoTrackerException
        """
        # Act
        exc = CoinGeckoException("test message")
        
        # Assert
        assert isinstance(exc, CryptoTrackerException)
        assert isinstance(exc, Exception)


# ══════════════════════════════════════════════════════════════════════
# TESTS : Exceptions CoinGecko
# ══════════════════════════════════════════════════════════════════════

class TestCoinGeckoExceptions:
    """Tests pour les exceptions liées à CoinGecko"""
    
    def test_rate_limit_exception_should_have_default_message(self):
        """
        GIVEN RateLimitException sans message
        WHEN elle est instanciée
        THEN un message par défaut est utilisé
        """
        # Act
        exc = RateLimitException()
        
        # Assert
        assert exc.message == "CoinGecko rate limit reached"
        assert str(exc) == "CoinGecko rate limit reached"
    
    def test_rate_limit_exception_should_accept_custom_message(self):
        """
        GIVEN RateLimitException avec message personnalisé
        WHEN elle est instanciée
        THEN le message personnalisé est utilisé
        """
        # Act
        exc = RateLimitException("Custom rate limit message")
        
        # Assert
        assert exc.message == "Custom rate limit message"
        assert str(exc) == "Custom rate limit message"
    
    def test_timeout_exception_should_have_default_message(self):
        """
        GIVEN TimeoutException sans message
        WHEN elle est instanciée
        THEN un message par défaut est utilisé
        """
        # Act
        exc = TimeoutException()
        
        # Assert
        assert exc.message == "CoinGecko API timeout"
        assert str(exc) == "CoinGecko API timeout"
    
    def test_timeout_exception_should_accept_custom_message(self):
        """
        GIVEN TimeoutException avec message personnalisé
        WHEN elle est instanciée
        THEN le message personnalisé est utilisé
        """
        # Act
        exc = TimeoutException("Custom timeout message")
        
        # Assert
        assert exc.message == "Custom timeout message"
    
    def test_api_exception_should_store_status_code(self):
        """
        GIVEN APIException avec status code
        WHEN elle est instanciée
        THEN le status code est stocké
        """
        # Act
        exc = APIException(500)
        
        # Assert
        assert exc.status_code == 500
        assert "status: 500" in exc.message
    
    def test_api_exception_should_format_message_with_status(self):
        """
        GIVEN APIException avec message personnalisé
        WHEN elle est instanciée
        THEN le message inclut le status code
        """
        # Act
        exc = APIException(404, "Resource not found")
        
        # Assert
        assert exc.status_code == 404
        assert exc.message == "Resource not found (status: 404)"


# ══════════════════════════════════════════════════════════════════════
# TESTS : Exceptions d'authentification
# ══════════════════════════════════════════════════════════════════════

class TestAuthenticationExceptions:
    """Tests pour les exceptions d'authentification"""
    
    def test_authentication_exception_should_inherit_from_base(self):
        """
        GIVEN AuthenticationException
        WHEN elle est instanciée
        THEN elle hérite de CryptoTrackerException
        """
        # Act
        exc = AuthenticationException("test")
        
        # Assert
        assert isinstance(exc, CryptoTrackerException)
    
    def test_invalid_credentials_exception_should_have_default_message(self):
        """
        GIVEN InvalidCredentialsException sans message
        WHEN elle est instanciée
        THEN un message par défaut est utilisé
        """
        # Act
        exc = InvalidCredentialsException()
        
        # Assert
        assert exc.message == "Invalid credentials"
    
    def test_invalid_credentials_exception_should_accept_custom_message(self):
        """
        GIVEN InvalidCredentialsException avec message personnalisé
        WHEN elle est instanciée
        THEN le message personnalisé est utilisé
        """
        # Act
        exc = InvalidCredentialsException("Wrong password")
        
        # Assert
        assert exc.message == "Wrong password"
    
    def test_token_expired_exception_should_have_default_message(self):
        """
        GIVEN TokenExpiredException sans message
        WHEN elle est instanciée
        THEN un message par défaut est utilisé
        """
        # Act
        exc = TokenExpiredException()
        
        # Assert
        assert exc.message == "Token has expired"
    
    def test_token_expired_exception_should_accept_custom_message(self):
        """
        GIVEN TokenExpiredException avec message personnalisé
        WHEN elle est instanciée
        THEN le message personnalisé est utilisé
        """
        # Act
        exc = TokenExpiredException("JWT expired 5 minutes ago")
        
        # Assert
        assert exc.message == "JWT expired 5 minutes ago"


# ══════════════════════════════════════════════════════════════════════
# TESTS : Exceptions de validation
# ══════════════════════════════════════════════════════════════════════

class TestValidationExceptions:
    """Tests pour les exceptions de validation"""
    
    def test_validation_exception_should_inherit_from_base(self):
        """
        GIVEN ValidationException
        WHEN elle est instanciée
        THEN elle hérite de CryptoTrackerException
        """
        # Act
        exc = ValidationException("test")
        
        # Assert
        assert isinstance(exc, CryptoTrackerException)
    
    def test_invalid_coin_id_exception_should_store_coin_id(self):
        """
        GIVEN InvalidCoinIdException avec coin_id
        WHEN elle est instanciée
        THEN le coin_id est stocké
        """
        # Act
        exc = InvalidCoinIdException("invalid-coin")
        
        # Assert
        assert exc.coin_id == "invalid-coin"
        assert "invalid-coin" in exc.message
    
    def test_invalid_coin_id_exception_should_format_message(self):
        """
        GIVEN InvalidCoinIdException
        WHEN elle est instanciée
        THEN le message est formaté correctement
        """
        # Act
        exc = InvalidCoinIdException("bad@coin#id")
        
        # Assert
        assert exc.message == "Invalid coin_id format: bad@coin#id"


# ══════════════════════════════════════════════════════════════════════
# TESTS : Conversion en HTTPException
# ══════════════════════════════════════════════════════════════════════

class TestToHttpException:
    """Tests pour la fonction to_http_exception"""
    
    def test_should_convert_rate_limit_exception_to_429(self):
        """
        GIVEN RateLimitException
        WHEN to_http_exception est appelé
        THEN HTTPException 429 est retournée
        """
        # Arrange
        exc = RateLimitException("Rate limit reached")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert http_exc.detail == "Rate limit reached"
    
    def test_should_convert_timeout_exception_to_504(self):
        """
        GIVEN TimeoutException
        WHEN to_http_exception est appelé
        THEN HTTPException 504 est retournée
        """
        # Arrange
        exc = TimeoutException("Request timeout")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_504_GATEWAY_TIMEOUT
        assert http_exc.detail == "Request timeout"
    
    def test_should_convert_api_exception_to_502(self):
        """
        GIVEN APIException
        WHEN to_http_exception est appelé
        THEN HTTPException 502 est retournée
        """
        # Arrange
        exc = APIException(500, "API error")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_502_BAD_GATEWAY
        assert "API error" in http_exc.detail
    
    def test_should_convert_invalid_credentials_to_401_with_header(self):
        """
        GIVEN InvalidCredentialsException
        WHEN to_http_exception est appelé
        THEN HTTPException 401 avec header WWW-Authenticate est retournée
        """
        # Arrange
        exc = InvalidCredentialsException("Bad credentials")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail == "Bad credentials"
        assert http_exc.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_should_convert_token_expired_to_401_with_header(self):
        """
        GIVEN TokenExpiredException
        WHEN to_http_exception est appelé
        THEN HTTPException 401 avec header WWW-Authenticate est retournée
        """
        # Arrange
        exc = TokenExpiredException("Token expired")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail == "Token expired"
        assert http_exc.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_should_convert_invalid_coin_id_to_400(self):
        """
        GIVEN InvalidCoinIdException
        WHEN to_http_exception est appelé
        THEN HTTPException 400 est retournée
        """
        # Arrange
        exc = InvalidCoinIdException("bad-coin")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "bad-coin" in http_exc.detail
    
    def test_should_convert_generic_exception_to_500(self):
        """
        GIVEN une exception générique CryptoTrackerException
        WHEN to_http_exception est appelé
        THEN HTTPException 500 est retournée
        """
        # Arrange
        exc = CryptoTrackerException("Unknown error")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail == "Unknown error"
    
    def test_should_handle_exception_without_message_attribute(self):
        """
        GIVEN une exception sans attribut message
        WHEN to_http_exception est appelé
        THEN l'exception est convertie en string
        """
        # Arrange
        exc = ValidationException("Validation failed")
        
        # Act
        http_exc = to_http_exception(exc)
        
        # Assert
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# ══════════════════════════════════════════════════════════════════════
# TESTS : Edge Cases
# ══════════════════════════════════════════════════════════════════════

class TestExceptionsEdgeCases:
    """Tests pour les cas limites des exceptions"""
    
    def test_exceptions_should_be_serializable(self):
        """
        GIVEN différentes exceptions
        WHEN elles sont converties en string
        THEN elles sont sérialisables
        """
        # Arrange
        exceptions = [
            RateLimitException("test"),
            TimeoutException("test"),
            APIException(500, "test"),
            InvalidCredentialsException("test"),
            TokenExpiredException("test"),
            InvalidCoinIdException("test-coin")
        ]
        
        # Act & Assert
        for exc in exceptions:
            assert str(exc)  # Should not raise
            assert repr(exc)  # Should not raise
    
    def test_api_exception_should_handle_various_status_codes(self):
        """
        GIVEN différents status codes
        WHEN APIException est créée
        THEN tous les codes sont acceptés
        """
        # Arrange
        status_codes = [400, 401, 403, 404, 500, 502, 503]
        
        # Act & Assert
        for code in status_codes:
            exc = APIException(code, "test")
            assert exc.status_code == code
            assert f"status: {code}" in exc.message
    
    def test_exceptions_should_preserve_inheritance_chain(self):
        """
        GIVEN toutes les exceptions personnalisées
        WHEN leur hiérarchie est vérifiée
        THEN la chaîne d'héritage est correcte
        """
        # Assert CoinGecko exceptions
        assert issubclass(RateLimitException, CoinGeckoException)
        assert issubclass(TimeoutException, CoinGeckoException)
        assert issubclass(APIException, CoinGeckoException)
        assert issubclass(CoinGeckoException, CryptoTrackerException)
        
        # Assert Authentication exceptions
        assert issubclass(InvalidCredentialsException, AuthenticationException)
        assert issubclass(TokenExpiredException, AuthenticationException)
        assert issubclass(AuthenticationException, CryptoTrackerException)
        
        # Assert Validation exceptions
        assert issubclass(InvalidCoinIdException, ValidationException)
        assert issubclass(ValidationException, CryptoTrackerException)
        
        # Assert base
        assert issubclass(CryptoTrackerException, Exception)
