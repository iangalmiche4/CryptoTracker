"""
holdings.py — Endpoints pour gérer les holdings (investissements)

Routes :
  GET    /api/holdings          - Liste tous les holdings de l'utilisateur
  POST   /api/holdings          - Créer un nouveau holding
  PUT    /api/holdings/{id}     - Mettre à jour un holding
  DELETE /api/holdings/{id}     - Supprimer un holding
  GET    /api/holdings/summary  - Statistiques du portfolio
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, cast

from database import get_db
from models import User, UserHolding
from schemas import HoldingCreate, HoldingUpdate, HoldingResponse, HoldingWithStats
from core.security import get_current_user
from services.coingecko_service import CoinGeckoService

router = APIRouter(prefix="/api/holdings", tags=["holdings"])
coingecko = CoinGeckoService()


@router.get("/", response_model=List[HoldingWithStats])
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les holdings de l'utilisateur avec statistiques"""
    holdings = db.query(UserHolding).filter(
        UserHolding.user_id == current_user.id
    ).all()
    
    if not holdings:
        return []
    
    # Récupérer les prix actuels
    coin_ids_list = sorted(set(str(h.coin_id) for h in holdings))
    coin_ids = ",".join(coin_ids_list)
    prices = await coingecko.get_prices(coin_ids)
    
    # Enrichir avec statistiques
    result = []
    for holding in holdings:
        current_price = prices.get(holding.coin_id, {}).get("usd", 0)
        quantity = cast(float, holding.quantity)
        purchase_price = cast(float, holding.purchase_price)
        current_value = quantity * current_price
        purchase_value = quantity * purchase_price
        total_gain_loss = current_value - purchase_value
        gain_loss_pct = (total_gain_loss / purchase_value) * 100 if purchase_price > 0 else 0
        
        result.append(HoldingWithStats(
            **holding.__dict__,
            current_price=current_price,
            current_value=current_value,
            total_gain_loss=total_gain_loss,
            gain_loss_percentage=gain_loss_pct
        ))
    
    return result


@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
def create_holding(
    holding_data: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un nouveau holding"""
    new_holding = UserHolding(
        user_id=current_user.id,
        **holding_data.model_dump()
    )
    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)
    return new_holding


@router.put("/{holding_id}", response_model=HoldingResponse)
def update_holding(
    holding_id: int,
    holding_data: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour un holding"""
    holding = db.query(UserHolding).filter(
        UserHolding.id == holding_id,
        UserHolding.user_id == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # Mettre à jour uniquement les champs fournis
    update_data = holding_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holding, field, value)
    
    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprimer un holding"""
    holding = db.query(UserHolding).filter(
        UserHolding.id == holding_id,
        UserHolding.user_id == current_user.id
    ).first()
    
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    db.delete(holding)
    db.commit()


@router.get("/summary")
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Statistiques globales du portfolio"""
    holdings = db.query(UserHolding).filter(
        UserHolding.user_id == current_user.id
    ).all()
    
    if not holdings:
        return {
            "total_invested": 0,
            "current_value": 0,
            "total_gain_loss": 0,
            "gain_loss_percentage": 0,
            "holdings_count": 0
        }
    
    # Récupérer les prix actuels
    coin_ids_list = sorted(set(str(h.coin_id) for h in holdings))
    coin_ids = ",".join(coin_ids_list)
    prices = await coingecko.get_prices(coin_ids)
    
    total_invested = sum(cast(float, h.quantity) * cast(float, h.purchase_price) for h in holdings)
    current_value = sum(
        cast(float, h.quantity) * prices.get(h.coin_id, {}).get("usd", 0)
        for h in holdings
    )
    total_gain_loss = current_value - total_invested
    gain_loss_pct = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0
    
    return {
        "total_invested": round(total_invested, 2),
        "current_value": round(current_value, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "gain_loss_percentage": round(gain_loss_pct, 2),
        "holdings_count": len(holdings)
    }
