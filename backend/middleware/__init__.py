"""
Middlewares pour CryptoTracker API

Ce package contient les middlewares personnalisés pour gérer
les aspects transversaux de l'application :
- Gestion globale des exceptions
- Logging des requêtes
- Rate limiting
- Optimisations CORS
"""

from .exception_handler import exception_handler_middleware
from .request_logging import request_logging_middleware

__all__ = [
    "exception_handler_middleware",
    "request_logging_middleware",
]

 
