# services/asset_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.assets import Asset, AssetClass, Allocation, Security, Holding
from services.service_base import BaseService
from datetime import datetime
import uuid

class AssetService(BaseService[Asset]):
    def __init__(self, db: Session):
        super().__init__(db, Asset)
    
    def get_client_assets(self, client_id: str):
        """Get all assets for a client"""
        assets = self.db.query(Asset).filter(Asset.client_id == client_id).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def get_account_assets(self, account_id: str):
        """Get all assets for an account"""
        assets = self.db.query(Asset).filter(Asset.account_id == account_id).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def get_plan_assets(self, plan_id: str):
        """Get all assets for a financial plan"""
        assets = self.db.query(Asset).filter(Asset.plan_id == plan_id).all()
        return [self._asset_to_dict(asset) for asset in assets]
    
    def get_asset_allocations(self, asset_id: str):
        """Get all allocations for an asset"""
        allocations = self.db.query(Allocation).filter(Allocation.asset_id == asset_id).all()
        return [self._allocation_to_dict(allocation) for allocation in allocations]
    
    def get_asset_holdings(self, asset_id: str):
        """Get all holdings for an asset"""
        holdings = self.db.query(Holding).filter(Holding.asset_id == asset_id).all()
        return [self._holding_to_dict(holding) for holding in holdings]
    
    # Added methods for Allocation
    def create_allocation(self, allocation_data: Dict[str, Any], user_id: str = None):
        """Create a new allocation"""
        if 'id' not in allocation_data:
            allocation_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in allocation_data:
            allocation_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in allocation_data:
            allocation_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in allocation_data:
                allocation_data['created_by'] = user_id
                
            if 'updated_by' not in allocation_data:
                allocation_data['updated_by'] = user_id
        
        allocation = Allocation(**allocation_data)
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        
        # Update other allocations to ensure the total is 100%
        if 'asset_id' in allocation_data:
            self.recalculate_asset_allocations(allocation_data['asset_id'])
        
        return self._allocation_to_dict(allocation)
    
    def update_allocation(self, allocation_id: str, allocation_data: Dict[str, Any], user_id: str = None):
        """Update an existing allocation"""
        allocation = self.db.query(Allocation).filter(Allocation.id == allocation_id).first()
        if not allocation:
            return None
            
        for key, value in allocation_data.items():
            if hasattr(allocation, key):
                setattr(allocation, key, value)
                
        allocation.updated_at = datetime.utcnow()
        
        if user_id:
            allocation.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(allocation)
        
        # Recalculate allocations for the asset
        self.recalculate_asset_allocations(allocation.asset_id)
        
        return self._allocation_to_dict(allocation)
    
    def delete_allocation(self, allocation_id: str):
        """Delete an allocation"""
        allocation = self.db.query(Allocation).filter(Allocation.id == allocation_id).first()
        if not allocation:
            return False
            
        asset_id = allocation.asset_id
            
        self.db.delete(allocation)
        self.db.commit()
        
        # Recalculate allocations for the asset
        self.recalculate_asset_allocations(asset_id)
        
        return True
    
    def recalculate_asset_allocations(self, asset_id: str):
        """Recalculate allocation percentages for an asset to ensure they sum to 100%"""
        allocations = self.db.query(Allocation).filter(Allocation.asset_id == asset_id).all()
        
        # Get the asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset or not allocations:
            return
        
        # Calculate total percentage
        total_percentage = sum(allocation.percentage or 0 for allocation in allocations)
        
        # If total is not 100%, adjust proportionally
        if abs(total_percentage - 100.0) > 0.01:  # Allow small rounding errors
            scale_factor = 100.0 / total_percentage if total_percentage > 0 else 0
            
            for allocation in allocations:
                allocation.percentage = (allocation.percentage or 0) * scale_factor
                allocation.value = (asset.value or 0) * (allocation.percentage / 100.0)
                
            self.db.commit()
        
        # Update the value fields based on percentages
        for allocation in allocations:
            allocation.value = (asset.value or 0) * (allocation.percentage / 100.0)
            
        self.db.commit()
    
    # Added methods for Security
    def get_all_securities(self, limit: int = 100, offset: int = 0):
        """Get all securities with pagination"""
        securities = self.db.query(Security).limit(limit).offset(offset).all()
        return [self._security_to_dict(security) for security in securities]
    
    def get_security_by_id(self, security_id: str):
        """Get security by ID"""
        security = self.db.query(Security).filter(Security.id == security_id).first()
        if not security:
            return None
        return self._security_to_dict(security)
    
    def get_security_by_symbol(self, symbol: str):
        """Get security by symbol"""
        security = self.db.query(Security).filter(Security.symbol == symbol).first()
        if not security:
            return None
        return self._security_to_dict(security)
    
    def create_security(self, security_data: Dict[str, Any], user_id: str = None):
        """Create a new security"""
        if 'id' not in security_data:
            security_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in security_data:
            security_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in security_data:
            security_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in security_data:
                security_data['created_by'] = user_id
                
            if 'updated_by' not in security_data:
                security_data['updated_by'] = user_id
                
        security = Security(**security_data)
        self.db.add(security)
        self.db.commit()
        self.db.refresh(security)
        
        return self._security_to_dict(security)
    
    def update_security(self, security_id: str, security_data: Dict[str, Any], user_id: str = None):
        """Update an existing security"""
        security = self.db.query(Security).filter(Security.id == security_id).first()
        if not security:
            return None
            
        for key, value in security_data.items():
            if hasattr(security, key):
                setattr(security, key, value)
                
        security.updated_at = datetime.utcnow()
        
        if user_id:
            security.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(security)
        
        # If price has changed, update all associated holdings
        if 'price' in security_data:
            self.update_holdings_for_security(security_id, security.price)
        
        return self._security_to_dict(security)
    
    def update_holdings_for_security(self, security_id: str, new_price: float):
        """Update the value of all holdings for a security based on a new price"""
        holdings = self.db.query(Holding).filter(Holding.security_id == security_id).all()
        
        for holding in holdings:
            holding.price = new_price
            holding.value = holding.shares * new_price
            
        self.db.commit()
        
        # Now update the total value of assets with these holdings
        assets_with_holdings = set()
        for holding in holdings:
            assets_with_holdings.add(holding.asset_id)
            
        for asset_id in assets_with_holdings:
            self.recalculate_asset_value(asset_id)
    
    def recalculate_asset_value(self, asset_id: str):
        """Recalculate the total value of an asset based on its holdings"""
        holdings = self.db.query(Holding).filter(Holding.asset_id == asset_id).all()
        
        total_value = sum(holding.value or 0 for holding in holdings)
        
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if asset:
            asset.value = total_value
            self.db.commit()
            
            # Also update allocation values
            self.recalculate_asset_allocations(asset_id)
    
    def create_holding(self, holding_data: Dict[str, Any], user_id: str = None):
        """Create a new holding"""
        if 'id' not in holding_data:
            holding_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in holding_data:
            holding_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in holding_data:
            holding_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in holding_data:
                holding_data['created_by'] = user_id
                
            if 'updated_by' not in holding_data:
                holding_data['updated_by'] = user_id
        
        # Calculate value if not provided
        if 'value' not in holding_data and 'shares' in holding_data and 'price' in holding_data:
            holding_data['value'] = holding_data['shares'] * holding_data['price']
        
        # Get the price from the security if not provided
        if 'price' not in holding_data and 'security_id' in holding_data:
            security = self.db.query(Security).filter(Security.id == holding_data['security_id']).first()
            if security:
                holding_data['price'] = security.price
                
                # Recalculate value if shares are provided
                if 'shares' in holding_data and 'value' not in holding_data:
                    holding_data['value'] = holding_data['shares'] * holding_data['price']
        
        holding = Holding(**holding_data)
        self.db.add(holding)
        self.db.commit()
        self.db.refresh(holding)
        
        # Update the asset value
        if 'asset_id' in holding_data:
            self.recalculate_asset_value(holding_data['asset_id'])
        
        return self._holding_to_dict(holding)
    
    def update_holding(self, holding_id: str, holding_data: Dict[str, Any], user_id: str = None):
        """Update an existing holding"""
        holding = self.db.query(Holding).filter(Holding.id == holding_id).first()
        if not holding:
            return None
            
        for key, value in holding_data.items():
            if hasattr(holding, key):
                setattr(holding, key, value)
        
        # Update the value based on shares and price
        if ('shares' in holding_data or 'price' in holding_data) and 'value' not in holding_data:
            holding.value = holding.shares * holding.price
        
        holding.updated_at = datetime.utcnow()
        
        if user_id:
            holding.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(holding)
        
        # Update the asset value
        self.recalculate_asset_value(holding.asset_id)
        
        return self._holding_to_dict(holding)
    
    def delete_holding(self, holding_id: str):
        """Delete a holding"""
        holding = self.db.query(Holding).filter(Holding.id == holding_id).first()
        if not holding:
            return False
            
        asset_id = holding.asset_id
            
        self.db.delete(holding)
        self.db.commit()
        
        # Update the asset value
        self.recalculate_asset_value(asset_id)
        
        return True
    
    def _asset_to_dict(self, asset: Asset) -> Dict[str, Any]:
        """Helper method to convert Asset model to dictionary"""
        return {
            "id": asset.id,
            "client_id": asset.client_id,
            "plan_id": asset.plan_id,
            "name": asset.name,
            "description": asset.description,
            "type": asset.type,
            "value": float(asset.value) if asset.value is not None else None,
            "basis": float(asset.basis) if asset.basis is not None else None,
            "growth_rate": float(asset.growth_rate) if asset.growth_rate is not None else None,
            "ownership": asset.ownership,
            "account_id": asset.account_id,
            "created_by": asset.created_by,
            "updated_by": asset.updated_by,
            "created_at": asset.created_at.isoformat() if asset.created_at else None,
            "updated_at": asset.updated_at.isoformat() if asset.updated_at else None
        }
    
    def _allocation_to_dict(self, allocation: Allocation) -> Dict[str, Any]:
        """Helper method to convert Allocation model to dictionary"""
        return {
            "id": allocation.id,
            "asset_id": allocation.asset_id,
            "asset_class_id": allocation.asset_class_id,
            "percentage": float(allocation.percentage) if allocation.percentage is not None else None,
            "value": float(allocation.value) if allocation.value is not None else None,
            "created_by": allocation.created_by,
            "updated_by": allocation.updated_by,
            "created_at": allocation.created_at.isoformat() if allocation.created_at else None,
            "updated_at": allocation.updated_at.isoformat() if allocation.updated_at else None
        }
    
    def _holding_to_dict(self, holding: Holding) -> Dict[str, Any]:
        """Helper method to convert Holding model to dictionary"""
        return {
            "id": holding.id,
            "asset_id": holding.asset_id,
            "security_id": holding.security_id,
            "shares": float(holding.shares) if holding.shares is not None else None,
            "price": float(holding.price) if holding.price is not None else None,
            "value": float(holding.value) if holding.value is not None else None,
            "basis": float(holding.basis) if holding.basis is not None else None,
            "created_by": holding.created_by,
            "updated_by": holding.updated_by,
            "created_at": holding.created_at.isoformat() if holding.created_at else None,
            "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
        }
    
    def _security_to_dict(self, security: Security) -> Dict[str, Any]:
        """Helper method to convert Security model to dictionary"""
        return {
            "id": security.id,
            "symbol": security.symbol,
            "name": security.name,
            "type": security.type,
            "price": float(security.price) if security.price is not None else None,
            "price_date": security.price_date.isoformat() if security.price_date else None,
            "asset_class_id": security.asset_class_id,
            "created_by": security.created_by,
            "updated_by": security.updated_by,
            "created_at": security.created_at.isoformat() if security.created_at else None,
            "updated_at": security.updated_at.isoformat() if security.updated_at else None
        }