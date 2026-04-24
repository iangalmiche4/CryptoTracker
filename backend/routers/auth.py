"""
auth.py — Routes d'authentification

Endpoints :
  POST /api/auth/register : Créer un nouveau compte
  POST /api/auth/login : Se connecter et obtenir un token JWT
  GET /api/auth/me : Récupérer les informations de l'utilisateur courant
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models import User
from schemas import UserRegister, Token, UserResponse
from core.security import hash_password, authenticate_user, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur.
    
    Args:
        user_data : Email + mot de passe
        db : Session de base de données
    
    Returns:
        Informations de l'utilisateur créé
    
    Raises:
        HTTPException 400 si l'email existe déjà
    """
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Créer le nouvel utilisateur
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Se connecter avec email + mot de passe.
    
    Args:
        form_data : Formulaire OAuth2 (username = email, password)
        db : Session de base de données
    
    Returns:
        Token JWT + type de token + expires_in
    
    Raises:
        HTTPException 401 si les identifiants sont incorrects
    """
    from config import settings
    
    # Authentifier l'utilisateur
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60  # En secondes
    }


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Récupérer les informations de l'utilisateur courant.
    
    Args:
        current_user : Utilisateur extrait du token JWT
    
    Returns:
        Informations de l'utilisateur
    """
    return current_user

 
