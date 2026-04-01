"""
security.py — Utilitaires de sécurité et authentification

Fonctions pour :
- Hachage et vérification des mots de passe (bcrypt)
- Création et validation des tokens JWT
- Dépendance FastAPI pour récupérer l'utilisateur courant

"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User


# ── Configuration ─────────────────────────────────────────────────────

# OAuth2 scheme pour extraire le token du header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Fonctions de hachage ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
    
    Returns:
        Hash bcrypt du mot de passe
    
    Note:
        Bcrypt has a 72-byte limit. Passwords are truncated if necessary.
    """
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe correspond à son hash
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Hash bcrypt stocké en base
    
    Returns:
        True si le mot de passe est correct, False sinon
    
    Note:
        Bcrypt has a 72-byte limit. Passwords are truncated if necessary.
    """
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ── Fonctions JWT ─────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT signé
    
    Args:
        data: Données à encoder dans le token (ex: {"sub": "user@example.com"})
        expires_delta: Durée de validité (défaut: settings.access_token_expire_minutes)
    
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Décode un token JWT et extrait l'email de l'utilisateur
    
    Args:
        token: Token JWT à décoder
    
    Returns:
        Email de l'utilisateur si le token est valide, None sinon
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None


# ── Dépendances FastAPI ───────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance FastAPI qui extrait l'utilisateur courant depuis le token JWT
    
    Usage dans un endpoint protégé :
        @app.get("/api/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return {"email": current_user.email}
    
    Args:
        token: Token JWT extrait du header Authorization
        db: Session de base de données
    
    Returns:
        Utilisateur authentifié
    
    Raises:
        HTTPException 401 si le token est invalide ou l'utilisateur n'existe pas
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Décoder le token
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception
    
    # Récupérer l'utilisateur en base
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


# ── Fonction d'authentification ──────────────────────────────────────

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec email + mot de passe
    
    Args:
        db: Session SQLAlchemy
        email: Email de l'utilisateur
        password: Mot de passe en clair
    
    Returns:
        Objet User si authentification réussie, None sinon
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, str(user.password_hash)):
        return None
    return user

 