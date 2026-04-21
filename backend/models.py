"""
models.py — Modèles SQLAlchemy pour la base de données

Tables :
  - users : Comptes utilisateurs avec authentification
  - user_coins : Coins suivis par chaque utilisateur (avec position pour drag & drop)
  - user_alerts : Alertes de prix configurées par utilisateur
  - user_holdings : Investissements crypto de l'utilisateur (portfolio)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# ── Enum pour les types d'alertes ─────────────────────────────────────

class AlertType(str, enum.Enum):
    """Type d'alerte : haute (prix monte) ou basse (prix descend)"""
    HIGH = "high"
    LOW = "low"


# ── Modèle User ───────────────────────────────────────────────────────

class User(Base):
    """
    Table users : Comptes utilisateurs
    
    Champs :
      - id : Clé primaire auto-incrémentée
      - email : Email unique (utilisé pour le login)
      - password_hash : Hash bcrypt du mot de passe
      - created_at : Date de création du compte
    
    Relations :
      - coins : Liste des coins suivis (user_coins)
      - alerts : Liste des alertes configurées (user_alerts)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    coins = relationship("UserCoin", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("UserAlert", back_populates="user", cascade="all, delete-orphan")
    holdings = relationship("UserHolding", back_populates="user", cascade="all, delete-orphan")


# ── Modèle UserCoin ───────────────────────────────────────────────────

class UserCoin(Base):
    """
    Table user_coins : Coins suivis par chaque utilisateur
    
    Champs :
      - id : Clé primaire auto-incrémentée
      - user_id : Référence vers users.id
      - coin_id : ID CoinGecko (ex: "bitcoin", "ethereum")
      - position : Position dans la liste (pour drag & drop)
      - created_at : Date d'ajout du coin
    
    Relations :
      - user : Utilisateur propriétaire
    
    Contraintes :
      - (user_id, coin_id) unique : un utilisateur ne peut pas suivre 2x le même coin
    """
    __tablename__ = "user_coins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(String, nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="coins")


# ── Modèle UserAlert ──────────────────────────────────────────────────

class UserAlert(Base):
    """
    Table user_alerts : Alertes de prix configurées par utilisateur
    
    Champs :
      - id : Clé primaire auto-incrémentée
      - user_id : Référence vers users.id
      - coin_id : ID CoinGecko (ex: "bitcoin")
      - type : Type d'alerte (HIGH ou LOW)
      - threshold : Seuil de prix en USD
      - created_at : Date de création de l'alerte
    
    Relations :
      - user : Utilisateur propriétaire
    
    Contraintes :
      - (user_id, coin_id, type) unique : un utilisateur ne peut avoir qu'une alerte HIGH et une LOW par coin
    """
    __tablename__ = "user_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(String, nullable=False, index=True)
    type = Column(Enum(AlertType), nullable=False)
    threshold = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="alerts")


# ── Modèle UserHolding ────────────────────────────────────────────────

class UserHolding(Base):
    """
    Table user_holdings : Investissements crypto de l'utilisateur
    
    Champs :
      - id : Clé primaire auto-incrémentée
      - user_id : Référence vers users.id
      - coin_id : ID CoinGecko (ex: "bitcoin", "ethereum")
      - quantity : Quantité possédée (ex: 0.5 BTC)
      - purchase_price : Prix d'achat en USD (ex: 45000)
      - purchase_date : Date d'achat
      - notes : Notes optionnelles (ex: "Achat DCA mensuel")
      - created_at : Date de création de l'entrée
      - updated_at : Date de dernière modification
    
    Relations :
      - user : Utilisateur propriétaire
    """
    __tablename__ = "user_holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    coin_id = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="holdings")


 
