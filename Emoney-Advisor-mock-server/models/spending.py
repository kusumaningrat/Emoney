#spending.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime, JSON, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base
from .enums import IncomeType, ExpenseCategory, FrequencyType

class Spending(Base):
    __tablename__ = "spending"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, nullable=False)
    annual_income = Column(Numeric(precision=15, scale=2))
    annual_expenses = Column(Numeric(precision=15, scale=2))
    annual_savings = Column(Numeric(precision=15, scale=2))
    monthly_income = Column(Numeric(precision=15, scale=2))
    monthly_expenses = Column(Numeric(precision=15, scale=2))
    monthly_savings = Column(Numeric(precision=15, scale=2))
    savings_rate = Column(Numeric(precision=6, scale=4))
    expense_to_income_ratio = Column(Numeric(precision=6, scale=4))
    cash_flow_status = Column(String)
    last_update = Column(Date)
    sync_status = Column(String)
    expense_categories = Column(JSON)
    linked_accounts = Column(JSON)
    analysis = Column(JSON)
    notes = Column(String)
    
    # Relationships
    client = relationship("Client", back_populates="spending_records")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    budgets = relationship("Budget", back_populates="spending")
    income_sources = relationship("Income", back_populates="spending")
    expenses = relationship("Expense", back_populates="spending")

class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    spending_id = Column(String, ForeignKey("spending.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    period_type = Column(String)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    total_income = Column(Numeric(precision=15, scale=2))
    total_expenses = Column(Numeric(precision=15, scale=2))
    total_savings = Column(Numeric(precision=15, scale=2))
    allocations = Column(JSON)
    category_limits = Column(JSON)
    progress = Column(JSON)
    auto_categorization = Column(Boolean, default=False)
    notifications = Column(JSON)
    notes = Column(String)
    
    # Relationships
    spending = relationship("Spending", back_populates="budgets")
    client = relationship("Client")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    categories = relationship("BudgetCategory", back_populates="budget")

class Income(Base):
    __tablename__ = "income"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    spending_id = Column(String, ForeignKey("spending.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    plan_id = Column(String, ForeignKey("financial_plans.id"), nullable=True)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    description = Column(Text)
    income_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    annual_amount = Column(Numeric(precision=15, scale=2))
    monthly_amount = Column(Numeric(precision=15, scale=2))
    amount_per_payment = Column(Numeric(precision=15, scale=2))
    payment_day = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    growth_rate = Column(Numeric(precision=6, scale=4))
    income_source = Column(JSON)
    taxable = Column(Boolean, default=True)
    tax_rate = Column(Numeric(precision=6, scale=4))
    notes = Column(String)
    
    # Relationships
    spending = relationship("Spending", back_populates="income_sources")
    client = relationship("Client", back_populates="income_sources")
    plan = relationship("FinancialPlan", foreign_keys=[plan_id], back_populates="income_sources")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    
    # Add these property and setter methods to handle the 'type' field
    @property
    def type(self):
        return self.income_type
        
    @type.setter
    def type(self, value):
        self.income_type = value
    
    @property
    def amount(self):
        """Backward compatibility - returns annual_amount"""
        return self.annual_amount
        
    @amount.setter
    def amount(self, value):
        """Backward compatibility - sets annual_amount"""
        self.annual_amount = value
        if not self.monthly_amount:
            self.monthly_amount = value / 12
        if not self.amount_per_payment:
            self.amount_per_payment = value / 12
        
    def __init__(self, **kwargs):
        """
        Initialize Income with backward compatibility for old field names
        """
        # Map 'type' to 'income_type'
        if 'type' in kwargs:
            kwargs['income_type'] = kwargs.pop('type')
        
        # Map 'amount' to the appropriate fields based on context
        if 'amount' in kwargs:
            amount_value = kwargs.pop('amount')
            
            # Get frequency to determine how to split the amount
            frequency = kwargs.get('frequency', 'Annual')
            
            # If annual_amount not already provided
            if 'annual_amount' not in kwargs:
                # If frequency is Annual, amount is the annual amount
                if frequency in ['Annual', 'Annually']:
                    kwargs['annual_amount'] = amount_value
                    if 'monthly_amount' not in kwargs:
                        kwargs['monthly_amount'] = amount_value / 12
                    if 'amount_per_payment' not in kwargs:
                        kwargs['amount_per_payment'] = amount_value
                # If frequency is Monthly, amount is the monthly amount
                elif frequency in ['Monthly']:
                    if 'monthly_amount' not in kwargs:
                        kwargs['monthly_amount'] = amount_value
                    kwargs['annual_amount'] = amount_value * 12
                    if 'amount_per_payment' not in kwargs:
                        kwargs['amount_per_payment'] = amount_value
                # For other frequencies, assume amount is annual
                else:
                    kwargs['annual_amount'] = amount_value
                    if 'monthly_amount' not in kwargs:
                        kwargs['monthly_amount'] = amount_value / 12
                    if 'amount_per_payment' not in kwargs:
                        # Calculate per payment based on frequency
                        payments_per_year = {
                            'Weekly': 52,
                            'Biweekly': 26,
                            'Quarterly': 4,
                            'Semi-Annual': 2
                        }.get(frequency, 12)
                        kwargs['amount_per_payment'] = amount_value / payments_per_year
        
        # Map 'is_taxable' to 'taxable'
        if 'is_taxable' in kwargs:
            kwargs['taxable'] = kwargs.pop('is_taxable')
        
        # Map 'owner' to something or remove it (Income model doesn't have 'owner' field)
        if 'owner' in kwargs:
            # Store in notes or ignore
            owner_value = kwargs.pop('owner')
            if 'notes' in kwargs and kwargs['notes']:
                kwargs['notes'] = f"Owner: {owner_value}. {kwargs['notes']}"
            else:
                kwargs['notes'] = f"Owner: {owner_value}"
        
        # Ensure required fields have defaults if not provided
        if 'status' not in kwargs:
            kwargs['status'] = 'active'
        
        if 'workspace_id' not in kwargs:
            kwargs['workspace_id'] = 'default-workspace'
        
        if 'created_by' not in kwargs:
            kwargs['created_by'] = 'system'
        
        if 'updated_by' not in kwargs:
            kwargs['updated_by'] = 'system'
        
        super().__init__(**kwargs)

class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    workspace_id = Column(String, nullable=False)
    spending_id = Column(String, ForeignKey("spending.id"))
    client_id = Column(String, ForeignKey("clients.id"))
    plan_id = Column(String, ForeignKey("financial_plans.id"), nullable=True)
    goal_id = Column(String, ForeignKey("goals.id"), nullable=True)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String, nullable=False)
    description = Column(Text)  # ADDED THIS FIELD
    category = Column(String, nullable=False)
    status = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    annual_amount = Column(Numeric(precision=15, scale=2))
    monthly_amount = Column(Numeric(precision=15, scale=2))
    amount_per_payment = Column(Numeric(precision=15, scale=2))
    payment_day = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    growth_rate = Column(Numeric(precision=6, scale=4))
    auto_payment = Column(Boolean, default=False)
    payment_method = Column(String)
    is_tax_deductible = Column(Boolean, default=False)
    expense_source = Column(JSON)
    is_discretionary = Column(Boolean, default=False)
    is_goal = Column(Boolean, default=False)
    notes = Column(String)
    
    # Relationships
    spending = relationship("Spending", back_populates="expenses")
    client = relationship("Client", back_populates="expenses")
    plan = relationship("FinancialPlan", back_populates="expenses")
    goal = relationship("Goal", back_populates="expenses")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")
    
    def __init__(self, **kwargs):
        """
        Initialize Expense with backward compatibility for old field names
        """
        # Map 'amount' to the appropriate fields based on context
        if 'amount' in kwargs:
            amount_value = kwargs.pop('amount')
            
            # Get frequency to determine how to split the amount
            frequency = kwargs.get('frequency', 'Monthly')
            
            # If monthly_amount not already provided
            if 'monthly_amount' not in kwargs:
                # If frequency is Monthly, amount is the monthly amount
                if frequency in ['Monthly']:
                    kwargs['monthly_amount'] = amount_value
                    kwargs['annual_amount'] = amount_value * 12
                    if 'amount_per_payment' not in kwargs:
                        kwargs['amount_per_payment'] = amount_value
                # If frequency is Annual, amount is the annual amount
                elif frequency in ['Annual', 'Annually']:
                    kwargs['annual_amount'] = amount_value
                    if 'monthly_amount' not in kwargs:
                        kwargs['monthly_amount'] = amount_value / 12
                    if 'amount_per_payment' not in kwargs:
                        kwargs['amount_per_payment'] = amount_value
                # For other frequencies, assume amount is monthly
                else:
                    kwargs['monthly_amount'] = amount_value
                    kwargs['annual_amount'] = amount_value * 12
                    if 'amount_per_payment' not in kwargs:
                        # Calculate per payment based on frequency
                        payments_per_year = {
                            'Weekly': 52,
                            'Biweekly': 26,
                            'Quarterly': 4,
                            'Semi-Annual': 2
                        }.get(frequency, 12)
                        kwargs['amount_per_payment'] = kwargs['annual_amount'] / payments_per_year
        
        # Map 'is_essential' to 'is_discretionary' (inverted logic)
        if 'is_essential' in kwargs:
            kwargs['is_discretionary'] = not kwargs.pop('is_essential')
        
        # Ensure required fields have defaults if not provided
        if 'status' not in kwargs:
            kwargs['status'] = 'active'
        
        if 'workspace_id' not in kwargs:
            kwargs['workspace_id'] = 'default-workspace'
        
        if 'created_by' not in kwargs:
            kwargs['created_by'] = 'system'
        
        if 'updated_by' not in kwargs:
            kwargs['updated_by'] = 'system'
        
        super().__init__(**kwargs)

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, index=True)
    budget_id = Column(String, ForeignKey("budgets.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    amount = Column(Float, nullable=False)
    created_by = Column(String, ForeignKey("users.id"))
    updated_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    budget = relationship("Budget", back_populates="categories")
    creator = relationship("User", foreign_keys=[created_by], overlaps="updater")
    updater = relationship("User", foreign_keys=[updated_by], overlaps="creator")