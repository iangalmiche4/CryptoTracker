"""
exceptions.py — Exceptions personnalisées de l'application

Définit des exceptions spécifiques pour améliorer la gestion d'erreurs
et faciliter le debugging.
"""

from fastapi import HTTPException, status


# ── Exceptions de base ────────────────────────────────────────────────

class CryptoTrackerException(Exception):
    """Exception de base pour toutes les exceptions de l'application"""
    pass


# ── Exceptions CoinGecko ──────────────────────────────────────────────

class CoinGeckoException(CryptoTrackerException):
    """Exception de base pour les erreurs liées à l'API CoinGecko"""
    pass


class RateLimitException(CoinGeckoException):
    """Exception levée quand le rate limit CoinGecko est atteint (429)"""
    def __init__(self, message: str = "CoinGecko rate limit reached"):
        self.message = message
        super().__init__(self.message)


class TimeoutException(CoinGeckoException):
    """Exception levée quand l'API CoinGecko ne répond pas à temps"""
    def __init__(self, message: str = "CoinGecko API timeout"):
        self.message = message
        super().__init__(self.message)


class APIException(CoinGeckoException):
    """Exception levée pour les erreurs génériques de l'API CoinGecko"""
    def __init__(self, status_code: int, message: str = "CoinGecko API error"):
        self.status_code = status_code
        self.message = f"{message} (status: {status_code})"
        super().__init__(self.message)


# ── Exceptions d'authentification ────────────────────────────────────

class AuthenticationException(CryptoTrackerException):
    """Exception de base pour les erreurs d'authentification"""
    pass


class InvalidCredentialsException(AuthenticationException):
    """Exception levée quand les identifiants sont incorrects"""
    def __init__(self, message: str = "Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class TokenExpiredException(AuthenticationException):
    """Exception levée quand le token JWT est expiré"""
    def __init__(self, message: str = "Token has expired"):
        self.message = message
        super().__init__(self.message)


# ── Exceptions de validation ──────────────────────────────────────────

class ValidationException(CryptoTrackerException):
    """Exception de base pour les erreurs de validation"""
    pass


class InvalidCoinIdException(ValidationException):
    """Exception levée quand le coin_id est invalide"""
    def __init__(self, coin_id: str):
        self.coin_id = coin_id
        self.message = f"Invalid coin_id format: {coin_id}"
        super().__init__(self.message)


# ── Fonctions utilitaires ─────────────────────────────────────────────

def to_http_exception(exc: CryptoTrackerException) -> HTTPException:
    """
    Convertit une exception personnalisée en HTTPException FastAPI
    
    Args:
        exc: Exception personnalisée
        
    Returns:
        HTTPException avec le code et message appropriés
    """
    if isinstance(exc, RateLimitException):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.message
        )
    
    if isinstance(exc, TimeoutException):
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=exc.message
        )
    
    if isinstance(exc, APIException):
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message
        )
    
    if isinstance(exc, InvalidCredentialsException):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if isinstance(exc, TokenExpiredException):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if isinstance(exc, InvalidCoinIdException):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message
        )
    
    # Exception générique
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc)
    )

 