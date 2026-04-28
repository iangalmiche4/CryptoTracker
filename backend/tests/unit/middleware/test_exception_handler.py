"""
Tests pour le middleware de gestion des exceptions
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from middleware.exception_handler import exception_handler_middleware
from core.exceptions import RateLimitException, TimeoutException, APIException


@pytest.fixture
def mock_request():
    """Crée une requête mock pour les tests"""
    request = Mock(spec=Request)
    request.method = "GET"
    request.url.path = "/api/test"
    request.client.host = "127.0.0.1"
    return request


@pytest.mark.asyncio
async def test_exception_handler_success(mock_request):
    """Test que le middleware laisse passer les requêtes réussies"""
    async def call_next(request):
        response = Mock()
        response.status_code = 200
        return response
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_exception_handler_rate_limit(mock_request):
    """Test la gestion de RateLimitException"""
    async def call_next(request):
        raise RateLimitException("Too many requests")
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_exception_handler_timeout(mock_request):
    """Test la gestion de TimeoutException"""
    async def call_next(request):
        raise TimeoutException("Request timeout")
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT


@pytest.mark.asyncio
async def test_exception_handler_api_exception(mock_request):
    """Test la gestion de APIException"""
    async def call_next(request):
        raise APIException(500, "External API error")
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_502_BAD_GATEWAY


@pytest.mark.asyncio
async def test_exception_handler_http_exception(mock_request):
    """Test que HTTPException est re-levée pour FastAPI"""
    async def call_next(request):
        raise HTTPException(status_code=404, detail="Not found")
    
    with pytest.raises(HTTPException) as exc_info:
        await exception_handler_middleware(mock_request, call_next)
    
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_exception_handler_generic_exception(mock_request):
    """Test la gestion des exceptions génériques"""
    async def call_next(request):
        raise ValueError("Unexpected error")
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_exception_handler_no_client(mock_request):
    """Test avec une requête sans client (edge case)"""
    mock_request.client = None
    
    async def call_next(request):
        raise RateLimitException("Too many requests")
    
    response = await exception_handler_middleware(mock_request, call_next)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_exception_handler_logging_rate_limit(mock_request):
    """Test que le logging fonctionne pour RateLimitException"""
    async def call_next(request):
        raise RateLimitException("Too many requests")
    
    with patch('middleware.exception_handler.logger') as mock_logger:
        await exception_handler_middleware(mock_request, call_next)
        mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
async def test_exception_handler_logging_timeout(mock_request):
    """Test que le logging fonctionne pour TimeoutException"""
    async def call_next(request):
        raise TimeoutException("Request timeout")
    
    with patch('middleware.exception_handler.logger') as mock_logger:
        await exception_handler_middleware(mock_request, call_next)
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_exception_handler_logging_api_exception(mock_request):
    """Test que le logging fonctionne pour APIException"""
    async def call_next(request):
        raise APIException(500, "External API error")
    
    with patch('middleware.exception_handler.logger') as mock_logger:
        await exception_handler_middleware(mock_request, call_next)
        mock_logger.error.assert_called_once()


@pytest.mark.asyncio
async def test_exception_handler_logging_generic(mock_request):
    """Test que le logging fonctionne pour les exceptions génériques"""
    async def call_next(request):
        raise ValueError("Unexpected error")
    
    with patch('middleware.exception_handler.logger') as mock_logger:
        await exception_handler_middleware(mock_request, call_next)
        mock_logger.exception.assert_called_once()

 
