"""
Exception Handler Middleware

Centralise la gestion des exceptions pour toute l'application.
Convertit les exceptions personnalisées en réponses HTTP appropriées
et log les erreurs de manière cohérente.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging

from core.exceptions import (
    RateLimitException,
    TimeoutException,
    APIException
)

logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next):
    """
    Middleware de gestion globale des exceptions.
    
    Gère :
    - RateLimitException (429)
    - TimeoutException (504)
    - APIException (502)
    - HTTPException (laisse FastAPI gérer)
    - Exception générique (500)
    
    Args:
        request: Requête FastAPI
        call_next: Fonction pour appeler le prochain middleware/handler
        
    Returns:
        Response appropriée selon le type d'exception
    """
    try:
        response = await call_next(request)
        return response
        
    except RateLimitException as e:
        logger.warning(
            f"Rate limit exceeded: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "error": str(e)
            }
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": str(e)}
        )
        
    except TimeoutException as e:
        logger.error(
            f"Timeout error: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "error": str(e)
            }
        )
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": str(e)}
        )
        
    except APIException as e:
        logger.error(
            f"External API error: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "error": str(e)
            }
        )
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": str(e)}
        )
        
    except HTTPException:
        # Laisser FastAPI gérer les HTTPException (auth, validation, etc.)
        raise
        
    except Exception as e:
        # Log complet avec stack trace pour les erreurs inattendues
        logger.exception(
            f"Unexpected error: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

 
