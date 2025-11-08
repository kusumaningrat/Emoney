"""fix_database_issues
Revision ID: 14543032e76e
Revises: 
Create Date: 2025-11-07 21:49:45.419929
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '14543032e76e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Fix index duplication and primary key constraint issues."""
    # Get a connection to the database
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # Fix the duplicate index issue
    if 'roles' in tables:
        print("Fixing roles table index...")
        # Drop the index if it exists
        op.execute("DROP INDEX IF EXISTS ix_roles_id")
        # Recreate it with IF NOT EXISTS to prevent future errors
        op.execute("CREATE INDEX IF NOT EXISTS ix_roles_id ON roles (id)")
    else:
        print("Roles table not found - skipping index fix")
    
    # Fix duplicate keys in firms table
    if 'firms' in tables:
        print("Checking for duplicate keys in firms table...")
        # Check for duplicates
        result = conn.execute(text("SELECT id, COUNT(*) FROM firms GROUP BY id HAVING COUNT(*) > 1"))
        rows = result.fetchall()
        
        if rows:
            print(f"Found {len(rows)} duplicate IDs in firms table. Fixing...")
            # Remove duplicates, keeping only the oldest record for each ID
            op.execute("""
            DELETE FROM firms 
            WHERE ctid NOT IN (
                SELECT MIN(ctid)
                FROM firms
                GROUP BY id
            )
            """)
            print("Duplicate records removed")
        else:
            print("No duplicates found in firms table")
    else:
        print("Firms table not found - skipping duplicate key fix")

def downgrade() -> None:
    """No downgrade necessary for this fix."""
    pass