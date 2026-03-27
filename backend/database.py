"""
database.py — Configuration de la base de données SQLAlchemy

Responsabilités :
  - Créer l'engine SQLAlchemy
  - Configurer la session factory
  - Fournir la dépendance get_db pour FastAPI
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de connexion PostgreSQL depuis .env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/cryptotracker")

# Engine SQLAlchemy avec pool de connexions
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_size=5,         # Nombre de connexions dans le pool
    max_overflow=10,     # Connexions supplémentaires si pool saturé
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


# ── Dépendance FastAPI ────────────────────────────────────────────────

def get_db():
    """
    Dépendance FastAPI qui fournit une session de base de données.
    
    Usage dans un endpoint :
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    
    La session est automatiquement fermée après la requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

 
