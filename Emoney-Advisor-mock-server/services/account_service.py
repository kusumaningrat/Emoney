# services/account_service.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models.accounts import Account, Liability, AccountTypeModel, Investment, Security
from models.enums import AccountType, OwnershipType, TaxStatus, LiabilityType
from services.service_base import BaseService
from datetime import datetime
import uuid

class AccountService(BaseService[Account]):
    def __init__(self, db: Session):
        super().__init__(db, Account)
    
    def get_client_accounts(self, client_id: str):
        """Get all accounts for a client"""
        accounts = self.db.query(Account).filter(Account.client_id == client_id).all()
        return [self._account_to_dict(account) for account in accounts]
    
    def get_account_liabilities(self, account_id: str):
        """Get all liabilities for an account"""
        liabilities = self.db.query(Liability).filter(Liability.account_id == account_id).all()
        return [self._liability_to_dict(liability) for liability in liabilities]
    
    def get_account_investments(self, account_id: str):
        """Get all investments for an account"""
        investments = self.db.query(Investment).filter(Investment.account_id == account_id).all()
        return [self._investment_to_dict(investment) for investment in investments]
    
    def get_all_account_types(self):
        """Get all account types"""
        account_types = self.db.query(AccountTypeModel).all()
        return [self._account_type_to_dict(account_type) for account_type in account_types]
    
    def get_account_type_by_id(self, account_type_id: str):
        """Get account type by ID"""
        account_type = self.db.query(AccountTypeModel).filter(AccountTypeModel.id == account_type_id).first()
        if not account_type:
            return None
        return self._account_type_to_dict(account_type)
    
    def get_investment_by_id(self, investment_id: str):
        """Get investment by ID"""
        investment = self.db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            return None
        return self._investment_to_dict(investment)
    
    def get_security_by_id(self, security_id: str):
        """Get security by ID"""
        security = self.db.query(Security).filter(Security.id == security_id).first()
        if not security:
            return None
        return self._security_to_dict(security)
    
    def get_security_by_ticker(self, ticker: str):
        """Get security by ticker symbol"""
        security = self.db.query(Security).filter(Security.ticker == ticker).first()
        if not security:
            return None
        return self._security_to_dict(security)
    
    def create_account_type(self, account_type_data: Dict[str, Any], user_id: str = None):
        """Create a new account type"""
        if 'id' not in account_type_data:
            account_type_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in account_type_data:
            account_type_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in account_type_data:
            account_type_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in account_type_data:
                account_type_data['created_by'] = user_id
                
            if 'updated_by' not in account_type_data:
                account_type_data['updated_by'] = user_id
                
        account_type = AccountTypeModel(**account_type_data)
        self.db.add(account_type)
        self.db.commit()
        self.db.refresh(account_type)
        
        return self._account_type_to_dict(account_type)
    
    def update_account_type(self, account_type_id: str, account_type_data: Dict[str, Any], user_id: str = None):
        """Update an existing account type"""
        account_type = self.db.query(AccountTypeModel).filter(AccountTypeModel.id == account_type_id).first()
        if not account_type:
            return None
            
        for key, value in account_type_data.items():
            if hasattr(account_type, key):
                setattr(account_type, key, value)
                
        account_type.updated_at = datetime.utcnow()
        
        if user_id:
            account_type.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(account_type)
        
        return self._account_type_to_dict(account_type)
    
    def create_investment(self, investment_data: Dict[str, Any], user_id: str = None):
        """Create a new investment"""
        if 'id' not in investment_data:
            investment_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in investment_data:
            investment_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in investment_data:
            investment_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in investment_data:
                investment_data['created_by'] = user_id
                
            if 'updated_by' not in investment_data:
                investment_data['updated_by'] = user_id
        
        # Calculate market value if not provided
        if 'market_value' not in investment_data and 'shares' in investment_data and 'current_price' in investment_data:
            investment_data['market_value'] = investment_data['shares'] * investment_data['current_price']
        
        investment = Investment(**investment_data)
        self.db.add(investment)
        self.db.commit()
        self.db.refresh(investment)
        
        # Update allocation percentages for all investments in this account
        if 'account_id' in investment_data:
            self.recalculate_account_allocations(investment_data['account_id'])
        
        return self._investment_to_dict(investment)
    
    def update_investment(self, investment_id: str, investment_data: Dict[str, Any], user_id: str = None):
        """Update an existing investment"""
        investment = self.db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            return None
            
        for key, value in investment_data.items():
            if hasattr(investment, key):
                setattr(investment, key, value)
                
        # Recalculate market value if shares or price was updated
        shares_updated = 'shares' in investment_data
        price_updated = 'current_price' in investment_data
        
        if (shares_updated or price_updated) and 'market_value' not in investment_data:
            investment.market_value = investment.shares * investment.current_price
                
        investment.updated_at = datetime.utcnow()
        
        if user_id:
            investment.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(investment)
        
        # Recalculate allocations for the account if shares or prices changed
        if shares_updated or price_updated or 'market_value' in investment_data:
            self.recalculate_account_allocations(investment.account_id)
        
        return self._investment_to_dict(investment)
    
    def delete_investment(self, investment_id: str):
        """Delete an investment"""
        investment = self.db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            return False
            
        account_id = investment.account_id
            
        self.db.delete(investment)
        self.db.commit()
        
        # Recalculate allocations for the account
        self.recalculate_account_allocations(account_id)
        
        return True
    
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
        
        return self._security_to_dict(security)
    
    def recalculate_account_allocations(self, account_id: str):
        """Recalculate allocation percentages for all investments in an account"""
        investments = self.db.query(Investment).filter(Investment.account_id == account_id).all()
        
        # Calculate total market value
        total_market_value = sum(investment.market_value or 0 for investment in investments)
        
        # Update allocation percentages
        if total_market_value > 0:
            for investment in investments:
                investment.allocation_percentage = ((investment.market_value or 0) / total_market_value) * 100
                
            self.db.commit()
    
    def create_liability(self, liability_data: Dict[str, Any], user_id: str = None):
        """Create a new liability"""
        if 'id' not in liability_data:
            liability_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in liability_data:
            liability_data['created_at'] = datetime.utcnow()
            
        if 'updated_at' not in liability_data:
            liability_data['updated_at'] = datetime.utcnow()
            
        if user_id:
            if 'created_by' not in liability_data:
                liability_data['created_by'] = user_id
                
            if 'updated_by' not in liability_data:
                liability_data['updated_by'] = user_id
                
        liability = Liability(**liability_data)
        self.db.add(liability)
        self.db.commit()
        self.db.refresh(liability)
        
        return self._liability_to_dict(liability)
    
    def update_liability(self, liability_id: str, liability_data: Dict[str, Any], user_id: str = None):
        """Update an existing liability"""
        liability = self.db.query(Liability).filter(Liability.id == liability_id).first()
        if not liability:
            return None
            
        for key, value in liability_data.items():
            if hasattr(liability, key):
                setattr(liability, key, value)
                
        liability.updated_at = datetime.utcnow()
        
        if user_id:
            liability.updated_by = user_id
            
        self.db.commit()
        self.db.refresh(liability)
        
        return self._liability_to_dict(liability)
    
    def _account_to_dict(self, account: Account) -> Dict[str, Any]:
        """Helper method to convert Account model to dictionary"""
        return {
            "id": account.id,
            "client_id": account.client_id,
            "name": account.name,
            "description": account.description,
            "institution": account.institution,
            "account_number": account.account_number,
            "type": account.type,
            "ownership": account.ownership,
            "tax_status": account.tax_status,
            "is_external": account.is_external,
            "created_by": account.created_by,
            "updated_by": account.updated_by,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None
        }
    
    def _liability_to_dict(self, liability: Liability) -> Dict[str, Any]:
        """Helper method to convert Liability model to dictionary"""
        return {
            "id": liability.id,
            "client_id": liability.client_id,
            "plan_id": liability.plan_id,
            "name": liability.name,
            "description": liability.description,
            "type": liability.type,
            "balance": float(liability.balance) if liability.balance is not None else None,
            "original_balance": float(liability.original_balance) if liability.original_balance is not None else None,
            "interest_rate": float(liability.interest_rate) if liability.interest_rate is not None else None,
            "payment_amount": float(liability.payment_amount) if liability.payment_amount is not None else None,
            "payment_frequency": liability.payment_frequency,
            "start_date": liability.start_date.isoformat() if liability.start_date else None,
            "end_date": liability.end_date.isoformat() if liability.end_date else None,
            "ownership": liability.ownership,
            "account_id": liability.account_id,
            "created_by": liability.created_by,
            "updated_by": liability.updated_by,
            "created_at": liability.created_at.isoformat() if liability.created_at else None,
            "updated_at": liability.updated_at.isoformat() if liability.updated_at else None
        }
        
    def _account_type_to_dict(self, account_type: AccountTypeModel) -> Dict[str, Any]:
        """Helper method to convert AccountTypeModel to dictionary"""
        return {
            "id": account_type.id,
            "name": account_type.name,
            "description": account_type.description,
            "category": account_type.category,
            "tax_treatment": account_type.tax_treatment,
            "is_retirement": account_type.is_retirement,
            "is_qualified": account_type.is_qualified,
            "is_custodial": account_type.is_custodial,
            "is_education": account_type.is_education,
            "is_health": account_type.is_health,
            "contribution_limits": account_type.contribution_limits,
            "withdrawal_rules": account_type.withdrawal_rules,
            "created_by": account_type.created_by,
            "updated_by": account_type.updated_by,
            "created_at": account_type.created_at.isoformat() if account_type.created_at else None,
            "updated_at": account_type.updated_at.isoformat() if account_type.updated_at else None
        }
    
    def _investment_to_dict(self, investment: Investment) -> Dict[str, Any]:
        """Helper method to convert Investment model to dictionary"""
        return {
            "id": investment.id,
            "account_id": investment.account_id,
            "security_id": investment.security_id,
            "name": investment.name,
            "ticker": investment.ticker,
            "asset_class": investment.asset_class,
            "investment_type": investment.investment_type,
            "shares": float(investment.shares) if investment.shares is not None else None,
            "purchase_price": float(investment.purchase_price) if investment.purchase_price is not None else None,
            "current_price": float(investment.current_price) if investment.current_price is not None else None,
            "purchase_date": investment.purchase_date.isoformat() if investment.purchase_date else None,
            "cost_basis": float(investment.cost_basis) if investment.cost_basis is not None else None,
            "market_value": float(investment.market_value) if investment.market_value is not None else None,
            "allocation_percentage": float(investment.allocation_percentage) if investment.allocation_percentage is not None else None,
            "yield_rate": float(investment.yield_rate) if investment.yield_rate is not None else None,
            "is_core_position": investment.is_core_position,
            "notes": investment.notes,
            "created_by": investment.created_by,
            "updated_by": investment.updated_by,
            "created_at": investment.created_at.isoformat() if investment.created_at else None,
            "updated_at": investment.updated_at.isoformat() if investment.updated_at else None
        }
    
    def _security_to_dict(self, security: Security) -> Dict[str, Any]:
        """Helper method to convert Security model to dictionary"""
        return {
            "id": security.id,
            "ticker": security.ticker,
            "name": security.name,
            "description": security.description,
            "security_type": security.security_type,
            "asset_class": security.asset_class,
            "sector": security.sector,
            "industry": security.industry,
            "risk_level": security.risk_level,
            "expense_ratio": float(security.expense_ratio) if security.expense_ratio is not None else None,
            "yield_rate": float(security.yield_rate) if security.yield_rate is not None else None,
            "benchmark": security.benchmark,
            "historical_performance": security.historical_performance,
            "key_metrics": security.key_metrics,
            "created_by": security.created_by,
            "updated_by": security.updated_by,
            "created_at": security.created_at.isoformat() if security.created_at else None,
            "updated_at": security.updated_at.isoformat() if security.updated_at else None
        }