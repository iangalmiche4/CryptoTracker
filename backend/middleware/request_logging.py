"""
Request Logging Middleware

Log automatiquement toutes les requêtes HTTP avec métriques de performance.
Ajoute un header X-Response-Time à chaque réponse.
"""

import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def request_logging_middleware(request: Request, call_next):
    """
    Middleware de logging des requêtes.
    
    Log :
    - Requête entrante (méthode, path, client)
    - Réponse sortante (status, durée)
    - Ajoute header X-Response-Time
    
    Args:
        request: Requête FastAPI
        call_next: Fonction pour appeler le prochain middleware/handler
        
    Returns:
        Response avec header X-Response-Time ajouté
    """
    start_time = time.time()
    
    # Log requête entrante
    logger.info(
        f"→ {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Traiter la requête
    response = await call_next(request)
    
    # Calculer la durée
    duration = time.time() - start_time
    
    # Log réponse avec temps
    log_level = logging.INFO if response.status_code < 400 else logging.WARNING
    logger.log(
        log_level,
        f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Ajouter header de temps de réponse
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    return response

 
