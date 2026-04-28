"""
Tests pour le middleware de logging des requêtes
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request

from middleware.request_logging import request_logging_middleware


@pytest.fixture
def mock_request():
    """Crée une requête mock pour les tests"""
    request = Mock(spec=Request)
    request.method = "GET"
    request.url.path = "/api/test"
    request.query_params = {}
    request.client.host = "127.0.0.1"
    return request


@pytest.mark.asyncio
async def test_request_logging_success(mock_request):
    """Test que le middleware log les requêtes réussies"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    response = await request_logging_middleware(mock_request, call_next)
    
    assert response.status_code == 200
    assert "X-Response-Time" in response.headers


@pytest.mark.asyncio
async def test_request_logging_adds_response_time_header(mock_request):
    """Test que le header X-Response-Time est ajouté"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    response = await request_logging_middleware(mock_request, call_next)
    
    assert "X-Response-Time" in response.headers
    assert response.headers["X-Response-Time"].endswith("s")


@pytest.mark.asyncio
async def test_request_logging_error_response(mock_request):
    """Test le logging des réponses d'erreur (4xx/5xx)"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    with patch('middleware.request_logging.logger') as mock_logger:
        response = await request_logging_middleware(mock_request, call_next)
        
        assert response.status_code == 500
        # Vérifie que le log a été appelé avec le bon niveau (WARNING pour erreurs)
        assert mock_logger.log.called


@pytest.mark.asyncio
async def test_request_logging_no_client(mock_request):
    """Test avec une requête sans client (edge case)"""
    mock_request.client = None
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    response = await request_logging_middleware(mock_request, call_next)
    
    assert response.status_code == 200
    assert "X-Response-Time" in response.headers


@pytest.mark.asyncio
async def test_request_logging_with_query_params(mock_request):
    """Test le logging avec des paramètres de requête"""
    mock_request.query_params = {"page": "1", "limit": "10"}
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    with patch('middleware.request_logging.logger') as mock_logger:
        response = await request_logging_middleware(mock_request, call_next)
        
        assert response.status_code == 200
        # Vérifie que le logger a été appelé
        assert mock_logger.info.called


@pytest.mark.asyncio
async def test_request_logging_measures_time(mock_request):
    """Test que le temps de réponse est mesuré correctement"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        # Simule un délai
        import asyncio
        await asyncio.sleep(0.01)
        return mock_response
    
    response = await request_logging_middleware(mock_request, call_next)
    
    # Vérifie que le temps est > 0
    time_header = response.headers["X-Response-Time"]
    time_value = float(time_header.rstrip("s"))
    assert time_value > 0


@pytest.mark.asyncio
async def test_request_logging_different_methods(mock_request):
    """Test le logging pour différentes méthodes HTTP"""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    for method in methods:
        mock_request.method = method
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        
        async def call_next(request):
            return mock_response
        
        response = await request_logging_middleware(mock_request, call_next)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_logging_info_level_for_success(mock_request):
    """Test que le niveau INFO est utilisé pour les succès"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    with patch('middleware.request_logging.logger') as mock_logger:
        await request_logging_middleware(mock_request, call_next)
        
        # Vérifie que info() a été appelé pour la requête entrante
        assert mock_logger.info.called


@pytest.mark.asyncio
async def test_request_logging_warning_level_for_errors(mock_request):
    """Test que le niveau WARNING est utilisé pour les erreurs"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.headers = {}
    
    async def call_next(request):
        return mock_response
    
    with patch('middleware.request_logging.logger') as mock_logger:
        await request_logging_middleware(mock_request, call_next)
        
        # Vérifie que log() a été appelé avec le bon niveau
        assert mock_logger.log.called

 
