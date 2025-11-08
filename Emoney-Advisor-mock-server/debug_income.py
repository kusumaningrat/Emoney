# debug_income.py
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models.spending import Income, Spending
import uuid
from datetime import datetime

# Create tables if they don't exist
Base.metadata.create_all(bind=engine, checkfirst=True)

def debug_create_income():
    """Create a single income record directly"""
    db = SessionLocal()
    try:
        # Get a spending record
        spending = db.query(Spending).first()
        if not spending:
            print("No spending records found. Create some first.")
            return
            
        print(f"Found spending record: {spending.id}")
        
        # Create a simple income record with minimal fields
        income_id = str(uuid.uuid4())
        
        # Print Income model columns
        print("Income model columns:")
        for column in Income.__table__.columns:
            print(f"- {column.name}: {column.type}")
        
        # Create income directly with constructor
        income = Income(
            id=f"income_test_{income_id}",
            workspace_id=spending.workspace_id,
            spending_id=spending.id,
            client_id=spending.client_id,
            created_by=spending.created_by,
            updated_by=spending.updated_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            name="Test Income",
            income_type="Salary",  # Using income_type
            status="Active",
            frequency="Monthly",
            annual_amount=50000.00,
            monthly_amount=4166.67,
            amount_per_payment=4166.67,
            taxable=True
        )
        
        print(f"Created income object: {income}")
        db.add(income)
        db.commit()
        print(f"Successfully added income with id: {income.id}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    debug_create_income()