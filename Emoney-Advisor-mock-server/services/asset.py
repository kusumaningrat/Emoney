# services/asset.py - Version 4: Asset Services


from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from models.account import Account, AccountType
from models.asset import Asset, AssetClass, Liability
from decimal import Decimal

class AssetService:
    """Service for Asset operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                account_id: Optional[str] = None, asset_class_id: Optional[str] = None,
                symbol: Optional[str] = None, status: Optional[str] = None) -> List[Asset]:
        """Get all assets with pagination and optional filters"""
        query = db.query(Asset)
        if account_id:
            query = query.filter(Asset.account_id == account_id)
        if asset_class_id:
            query = query.filter(Asset.asset_class_id == asset_class_id)
        if symbol:
            query = query.filter(Asset.symbol.ilike(f"%{symbol}%"))
        if status:
            query = query.filter(Asset.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, asset_id: str) -> Optional[Asset]:
        """Get asset by ID with account and asset class details"""
        return db.query(Asset).options(
            joinedload(Asset.account),
            joinedload(Asset.asset_class)
        ).filter(Asset.asset_id == asset_id).first()
    
    def get_asset_performance(self, db: Session, asset_id: str,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> dict:
        """Get asset performance metrics"""
        asset = self.get_by_id(db, asset_id)
        if not asset:
            return {}
        
        return {
            "asset_id": asset_id,
            "security_name": asset.security_name,
            "symbol": asset.symbol,
            "shares": asset.shares,
            "current_price": asset.price,
            "current_value": asset.value,
            "cost_basis": asset.cost_basis,
            "unrealized_gain": asset.unrealized_gain,
            "unrealized_gain_percent": asset.unrealized_gain_percent,
            "asset_class": asset.asset_class.class_name if asset.asset_class else None,
            "as_of_date": asset.as_of_date
        }


class AssetClassService:
    """Service for Asset Class operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                category: Optional[str] = None, risk_level: Optional[str] = None,
                status: Optional[str] = None) -> List[AssetClass]:
        """Get all asset classes with pagination and optional filters"""
        query = db.query(AssetClass)
        if category:
            query = query.filter(AssetClass.category == category)
        if risk_level:
            query = query.filter(AssetClass.risk_level == risk_level)
        if status:
            query = query.filter(AssetClass.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, asset_class_id: str) -> Optional[AssetClass]:
        """Get asset class by ID with related assets"""
        return db.query(AssetClass).options(
            joinedload(AssetClass.assets)
        ).filter(AssetClass.asset_class_id == asset_class_id).first()
    
    def get_by_class_name(self, db: Session, class_name: str) -> Optional[AssetClass]:
        """Get asset class by name"""
        return db.query(AssetClass).filter(
            AssetClass.class_name == class_name
        ).first()


class LiabilityService:
    """Service for Liability operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, household_id: Optional[str] = None,
                liability_type: Optional[str] = None, status: Optional[str] = None) -> List[Liability]:
        """Get all liabilities with pagination and optional filters"""
        query = db.query(Liability)
        if client_id:
            query = query.filter(Liability.client_id == client_id)
        if household_id:
            query = query.filter(Liability.household_id == household_id)
        if liability_type:
            query = query.filter(Liability.liability_type == liability_type)
        if status:
            query = query.filter(Liability.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, liability_id: str) -> Optional[Liability]:
        """Get liability by ID with client and household details"""
        return db.query(Liability).options(
            joinedload(Liability.client),
            joinedload(Liability.household)
        ).filter(Liability.liability_id == liability_id).first()
    
    def get_liability_schedule(self, db: Session, liability_id: str) -> dict:
        """Get payment schedule for a liability (basic calculation)"""
        liability = self.get_by_id(db, liability_id)
        if not liability:
            return {}
        
        # Basic amortization calculation (simplified)
        balance = liability.current_balance or 0
        monthly_payment = liability.monthly_payment or 0
        interest_rate = liability.interest_rate or 0
        
        if monthly_payment <= 0 or balance <= 0:
            return {}
        
        # Calculate remaining payments (simplified)
        monthly_interest_rate = interest_rate / 12 / 100
        remaining_payments = 0
        temp_balance = balance
        
        while temp_balance > 0 and remaining_payments < 360:  # Max 30 years
            interest_payment = temp_balance * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment
            if principal_payment <= 0:
                break
            temp_balance -= principal_payment
            remaining_payments += 1
        
        return {
            "liability_id": liability_id,
            "liability_name": liability.liability_name,
            "current_balance": balance,
            "monthly_payment": monthly_payment,
            "interest_rate": interest_rate,
            "remaining_payments": remaining_payments,
            "estimated_payoff_months": remaining_payments,
            "total_interest_remaining": (monthly_payment * remaining_payments) - balance
        }