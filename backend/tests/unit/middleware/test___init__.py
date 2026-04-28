"""
Tests pour le module middleware __init__
"""

import pytest

def test_middleware_imports():
    """Test que les middlewares sont correctement importés"""
    from middleware import exception_handler_middleware, request_logging_middleware  # type: ignore
    
    assert exception_handler_middleware is not None
    assert request_logging_middleware is not None


def test_middleware_all_exports():
    """Test que __all__ contient les exports attendus"""
    import middleware  # type: ignore
    
    assert hasattr(middleware, '__all__')
    assert 'exception_handler_middleware' in middleware.__all__  # type: ignore
    assert 'request_logging_middleware' in middleware.__all__  # type: ignore


def test_middleware_callable():
    """Test que les middlewares sont des callables"""
    from middleware import exception_handler_middleware, request_logging_middleware  # type: ignore
    
    assert callable(exception_handler_middleware)
    assert callable(request_logging_middleware)

 
