"""
Tests pour schemas.py - Validation des schémas Pydantic et fonctions utilitaires
"""

import pytest
from schemas import create_links, Link, Links


class TestCreateLinks:
    """Tests pour la fonction create_links"""
    
    def test_create_links_for_collection(self):
        """
        GIVEN une URL de base sans resource_id
        WHEN create_links est appelé
        THEN les liens de collection sont générés (self, create)
        """
        # Act
        links = create_links("/api/users")
        
        # Assert
        assert links.self is not None
        assert links.self.href == "/api/users"
        assert links.self.method == "GET"
        assert links.self.rel == "self"
        
        assert links.create is not None
        assert links.create.href == "/api/users"
        assert links.create.method == "POST"
        assert links.create.rel == "create"
        
        assert links.update is None
        assert links.delete is None
        assert links.collection is None
    
    def test_create_links_for_individual_resource(self):
        """
        GIVEN une URL de base avec un resource_id
        WHEN create_links est appelé
        THEN les liens de ressource individuelle sont générés (self, update, delete, collection)
        """
        # Act
        links = create_links("/api/users", resource_id=123)
        
        # Assert
        assert links.self is not None
        assert links.self.href == "/api/users/123"
        assert links.self.method == "GET"
        assert links.self.rel == "self"
        
        assert links.update is not None
        assert links.update.href == "/api/users/123"
        assert links.update.method == "PUT"
        assert links.update.rel == "update"
        
        assert links.delete is not None
        assert links.delete.href == "/api/users/123"
        assert links.delete.method == "DELETE"
        assert links.delete.rel == "delete"
        
        assert links.collection is not None
        assert links.collection.href == "/api/users"
        assert links.collection.method == "GET"
        assert links.collection.rel == "collection"
        
        assert links.create is None
    
    def test_create_links_with_related_resources(self):
        """
        GIVEN une URL de base avec des ressources liées
        WHEN create_links est appelé avec related
        THEN les liens related sont ajoutés
        """
        # Arrange
        related = {
            "posts": "/api/users/123/posts",
            "comments": "/api/users/123/comments"
        }
        
        # Act
        links = create_links("/api/users", resource_id=123, related=related)
        
        # Assert
        assert links.related is not None
        assert "posts" in links.related
        assert links.related["posts"].href == "/api/users/123/posts"
        assert links.related["posts"].method == "GET"
        assert links.related["posts"].rel == "posts"
        
        assert "comments" in links.related
        assert links.related["comments"].href == "/api/users/123/comments"
        assert links.related["comments"].method == "GET"
        assert links.related["comments"].rel == "comments"
    
    def test_create_links_for_collection_with_related(self):
        """
        GIVEN une URL de collection avec des ressources liées
        WHEN create_links est appelé
        THEN les liens de collection et related sont générés
        """
        # Arrange
        related = {
            "stats": "/api/users/stats"
        }
        
        # Act
        links = create_links("/api/users", related=related)
        
        # Assert
        assert links.self is not None
        assert links.create is not None
        assert links.related is not None
        assert "stats" in links.related
        assert links.related["stats"].href == "/api/users/stats"
    
    def test_create_links_without_related(self):
        """
        GIVEN une URL sans ressources liées
        WHEN create_links est appelé sans related
        THEN related est None
        """
        # Act
        links = create_links("/api/users", resource_id=123)
        
        # Assert
        assert links.related is None
    
    def test_create_links_with_empty_related(self):
        """
        GIVEN une URL avec un dictionnaire related vide
        WHEN create_links est appelé
        THEN related est None (car le dict est vide, la condition if related est False)
        """
        # Act
        links = create_links("/api/users", related={})
        
        # Assert
        assert links.related is None
    
    def test_create_links_returns_links_object(self):
        """
        GIVEN n'importe quelle URL
        WHEN create_links est appelé
        THEN un objet Links est retourné
        """
        # Act
        links = create_links("/api/test")
        
        # Assert
        assert isinstance(links, Links)
    
    def test_create_links_with_numeric_resource_id(self):
        """
        GIVEN un resource_id numérique
        WHEN create_links est appelé
        THEN les liens sont générés correctement
        """
        # Act
        links = create_links("/api/coins", resource_id=42)
        
        # Assert
        assert links.self is not None
        assert links.self.href == "/api/coins/42"
        assert links.update is not None
        assert links.update.href == "/api/coins/42"
        assert links.delete is not None
        assert links.delete.href == "/api/coins/42"

 