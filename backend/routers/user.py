"""
user.py — Routes pour les données utilisateur (coins et alertes)

Endpoints :
  GET /api/user/data : Récupérer toutes les données utilisateur (coins + alertes)
  
  POST /api/user/coins : Ajouter un coin à suivre
  PUT /api/user/coins/reorder : Réorganiser les coins (drag & drop)
  DELETE /api/user/coins/{coin_id} : Supprimer un coin
  
  POST /api/user/alerts : Créer une alerte
  PUT /api/user/alerts/{alert_id} : Modifier une alerte
  DELETE /api/user/alerts/{alert_id} : Supprimer une alerte
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, UserCoin, UserAlert, AlertType
from schemas import (
    UserDataResponse, UserResponse,
    CoinCreate, CoinResponse, CoinsReorder,
    AlertCreate, AlertUpdate, AlertResponse
)
from core.security import get_current_user

router = APIRouter(prefix="/api/user", tags=["User Data"])


# ── Endpoint global ───────────────────────────────────────────────────

@router.get("/data", response_model=UserDataResponse)
def get_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer toutes les données de l'utilisateur courant.
    
    Returns:
        - Informations utilisateur
        - Liste des coins suivis (ordonnée par position)
        - Liste des alertes configurées
    """
    # Récupérer les coins ordonnés par position
    coins = db.query(UserCoin).filter(
        UserCoin.user_id == current_user.id
    ).order_by(UserCoin.position).all()
    
    # Récupérer les alertes
    alerts = db.query(UserAlert).filter(
        UserAlert.user_id == current_user.id
    ).all()
    
    return {
        "user": current_user,
        "coins": coins,
        "alerts": alerts
    }


# ── Endpoints Coins ───────────────────────────────────────────────────

@router.post("/coins", response_model=CoinResponse, status_code=status.HTTP_201_CREATED)
def add_coin(
    coin_data: CoinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ajouter un coin à la liste de suivi.
    
    Args:
        coin_data : ID du coin + position optionnelle
    
    Returns:
        Coin créé
    
    Raises:
        HTTPException 400 si le coin est déjà suivi
    """
    # Vérifier si le coin n'est pas déjà suivi
    existing = db.query(UserCoin).filter(
        UserCoin.user_id == current_user.id,
        UserCoin.coin_id == coin_data.coin_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coin already tracked"
        )
    
    # Déterminer la position
    if coin_data.position is None:
        # Ajouter à la fin
        max_position = db.query(UserCoin).filter(
            UserCoin.user_id == current_user.id
        ).count()
        position = max_position
    else:
        position = coin_data.position
    
    # Créer le coin
    new_coin = UserCoin(
        user_id=current_user.id,
        coin_id=coin_data.coin_id,
        position=position
    )
    db.add(new_coin)
    db.commit()
    db.refresh(new_coin)
    
    return new_coin


@router.put("/coins/reorder")
def reorder_coins(
    reorder_data: CoinsReorder,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Réorganiser les coins après un drag & drop.
    
    Args:
        reorder_data : Liste ordonnée des coin_ids
    
    Returns:
        Message de succès
    """
    # Récupérer tous les coins de l'utilisateur
    user_coins = db.query(UserCoin).filter(
        UserCoin.user_id == current_user.id
    ).all()
    
    # Créer un mapping coin_id -> UserCoin
    coins_map: dict[str, UserCoin] = {str(coin.coin_id): coin for coin in user_coins}
    
    # Mettre à jour les positions
    for index, coin_id in enumerate(reorder_data.coin_ids):
        if coin_id in coins_map:
            setattr(coins_map[coin_id], 'position', index)
    
    db.commit()
    
    return {"message": "Coins reordered successfully"}


@router.delete("/coins/{coin_id}")
def remove_coin(
    coin_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer un coin de la liste de suivi.
    
    Args:
        coin_id : ID CoinGecko du coin à supprimer
    
    Returns:
        Message de succès
    
    Raises:
        HTTPException 404 si le coin n'est pas trouvé
    """
    coin = db.query(UserCoin).filter(
        UserCoin.user_id == current_user.id,
        UserCoin.coin_id == coin_id
    ).first()
    
    if not coin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coin not found"
        )
    
    db.delete(coin)
    db.commit()
    
    return {"message": "Coin removed successfully"}


# ── Endpoints Alerts ──────────────────────────────────────────────────

@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Créer une alerte de prix.
    
    Args:
        alert_data : coin_id, type (high/low), threshold
    
    Returns:
        Alerte créée
    
    Raises:
        HTTPException 400 si une alerte du même type existe déjà pour ce coin
    """
    # Vérifier qu'une alerte du même type n'existe pas déjà
    existing = db.query(UserAlert).filter(
        UserAlert.user_id == current_user.id,
        UserAlert.coin_id == alert_data.coin_id,
        UserAlert.type == alert_data.type
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Alert {alert_data.type} already exists for this coin"
        )
    
    # Créer l'alerte
    new_alert = UserAlert(
        user_id=current_user.id,
        coin_id=alert_data.coin_id,
        type=AlertType(alert_data.type),
        threshold=alert_data.threshold
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return new_alert


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Modifier le seuil d'une alerte existante.
    
    Args:
        alert_id : ID de l'alerte
        alert_data : Nouveau seuil
    
    Returns:
        Alerte mise à jour
    
    Raises:
        HTTPException 404 si l'alerte n'existe pas
    """
    alert = db.query(UserAlert).filter(
        UserAlert.id == alert_id,
        UserAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    setattr(alert, 'threshold', alert_data.threshold)
    db.commit()
    db.refresh(alert)
    
    return alert


@router.delete("/alerts/{alert_id}")
def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer une alerte.
    
    Args:
        alert_id : ID de l'alerte
    
    Returns:
        Message de succès
    
    Raises:
        HTTPException 404 si l'alerte n'existe pas
    """
    alert = db.query(UserAlert).filter(
        UserAlert.id == alert_id,
        UserAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}

 
