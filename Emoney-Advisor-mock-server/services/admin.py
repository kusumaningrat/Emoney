# services/admin.py

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from database import Base, engine
from typing import Dict, Any, Optional
from datetime import datetime

# Import seeders
from seeders.identity_seeder import IdentitySeeder
# from seeders.client_seeder import ClientSeeder  # To be created for V2
# from seeders.planning_seeder import PlanningSeeder  # To be created for V3

# Import all V1 models to ensure they're registered with Base
from models.identity import (
    User, Office, Role, Permission, SharingRule, Logon
)

class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def seed_database(self, entity_type: str = "all") -> Dict[str, Any]:
        """
        Seed the database with test data based on entity_type.
        
        Args:
            entity_type: Type of entities to seed ("all", "identity", "clients", "planning")
        
        Returns:
            Dictionary with seeding results
        """
        try:
            results = {
                "status": "success",
                "entity_type": entity_type,
                "seeded_entities": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if entity_type in ["all", "identity"]:
                print("Seeding Identity (V1) data...")
                identity_seeder = IdentitySeeder(self.db)
                identity_data = identity_seeder.seed_all()
                
                results["seeded_entities"]["identity"] = {
                    "users": len(identity_data.get("users", [])),
                    "offices": len(identity_data.get("offices", [])),
                    "roles": len(identity_data.get("roles", [])),
                    "permissions": len(identity_data.get("permissions", [])),
                    "sharing_rules": len(identity_data.get("sharing_rules", [])),
                    "logons": len(identity_data.get("logons", []))
                }
            
            # Future versions
            # if entity_type in ["all", "clients"]:
            #     print("Seeding Client (V2) data...")
            #     client_seeder = ClientSeeder(self.db)
            #     client_data = client_seeder.seed_all()
            #     results["seeded_entities"]["clients"] = {...}
            
            # if entity_type in ["all", "planning"]:
            #     print("Seeding Planning (V3) data...")
            #     planning_seeder = PlanningSeeder(self.db)
            #     planning_data = planning_seeder.seed_all()
            #     results["seeded_entities"]["planning"] = {...}
            
            return results
            
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "entity_type": entity_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def reset_database(self) -> Dict[str, Any]:
        """
        Drop all tables and recreate them.
        
        WARNING: This will delete ALL data in the database!
        
        Returns:
            Dictionary with reset results
        """
        try:
            print("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            
            print("Creating all tables...")
            Base.metadata.create_all(bind=engine)
            
            # Get list of created tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            return {
                "status": "success",
                "message": "Database reset successfully",
                "tables_created": len(tables),
                "tables": tables,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to reset database",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get database status including table counts and basic statistics.
        
        Returns:
            Dictionary with database status information
        """
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            table_counts = {}
            
            # Count records in each table
            for table in tables:
                try:
                    result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    table_counts[table] = count
                except Exception as e:
                    table_counts[table] = f"Error: {str(e)}"
            
            # Calculate totals by version
            v1_identity_tables = [
                "users", "offices", "roles", "permissions",
                "user_roles", "role_permissions", "sharing_rules", "logons"
            ]
            
            v2_client_tables = [
                "clients", "contacts", "households", "spouses", "relationships"
            ]
            
            v3_planning_tables = [
                "financial_plans", "goals", "scenarios", "cash_flows", "net_worths"
            ]
            
            def sum_counts(table_list):
                return sum(
                    table_counts.get(table, 0) 
                    for table in table_list 
                    if isinstance(table_counts.get(table), int)
                )
            
            return {
                "status": "success",
                "database": {
                    "total_tables": len(tables),
                    "tables": tables
                },
                "record_counts": {
                    "by_table": table_counts,
                    "by_version": {
                        "v1_identity": sum_counts(v1_identity_tables),
                        "v2_clients": sum_counts(v2_client_tables),
                        "v3_planning": sum_counts(v3_planning_tables),
                        "total": sum(
                            count for count in table_counts.values() 
                            if isinstance(count, int)
                        )
                    }
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to get database status",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def verify_seeding(self) -> Dict[str, Any]:
        """
        Verify that seeding was successful by checking expected counts.
        
        Returns:
            Dictionary with verification results
        """
        try:
            expected_counts = {
                # V1 - Identity & Access Management
                "users": 60,
                "offices": 15,
                "roles": 10,
                "permissions": 50,
                "sharing_rules": 80,
                "logons": 100,
                # V2 - Client & Household (when implemented)
                # "clients": 250,
                # "households": 150,
                # "spouses": 180,
                # "contacts": 100,
                # "relationships": 120,
                # V3 - Financial Planning (when implemented)
                # "financial_plans": 200,
                # "goals": 800,
                # "scenarios": 150,
            }
            
            verification_results = {}
            all_passed = True
            
            for table, expected in expected_counts.items():
                try:
                    result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    actual = result.scalar()
                    passed = actual == expected
                    
                    verification_results[table] = {
                        "expected": expected,
                        "actual": actual,
                        "passed": passed
                    }
                    
                    if not passed:
                        all_passed = False
                        
                except Exception as e:
                    verification_results[table] = {
                        "expected": expected,
                        "actual": None,
                        "passed": False,
                        "error": str(e)
                    }
                    all_passed = False
            
            return {
                "status": "success" if all_passed else "warning",
                "message": "All checks passed" if all_passed else "Some checks failed",
                "verification": verification_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to verify seeding",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def truncate_all_tables(self) -> Dict[str, Any]:
        """
        Truncate all tables (delete all data but keep structure).
        Faster than drop/create for testing.
        
        Returns:
            Dictionary with truncation results
        """
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Disable foreign key checks temporarily (SQLite uses PRAGMA)
            try:
                # For MySQL/MariaDB
                self.db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            except:
                # For PostgreSQL
                try:
                    self.db.execute(text("SET session_replication_role = 'replica'"))
                except:
                    # For SQLite
                    self.db.execute(text("PRAGMA foreign_keys = OFF"))
            
            truncated_tables = []
            for table in tables:
                try:
                    self.db.execute(text(f"DELETE FROM {table}"))
                    truncated_tables.append(table)
                except Exception as e:
                    print(f"Failed to truncate {table}: {str(e)}")
            
            # Re-enable foreign key checks
            try:
                self.db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            except:
                try:
                    self.db.execute(text("SET session_replication_role = 'origin'"))
                except:
                    self.db.execute(text("PRAGMA foreign_keys = ON"))
            
            self.db.commit()
            
            return {
                "status": "success",
                "message": "All tables truncated successfully",
                "truncated_tables": len(truncated_tables),
                "tables": truncated_tables,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "message": "Failed to truncate tables",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific table.
        
        Args:
            table_name: Name of the table to inspect
        
        Returns:
            Dictionary with table information
        """
        try:
            inspector = inspect(engine)
            
            # Get columns
            columns = inspector.get_columns(table_name)
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            
            # Get record count
            result = self.db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            record_count = result.scalar()
            
            return {
                "status": "success",
                "table_name": table_name,
                "record_count": record_count,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": col.get("default")
                    }
                    for col in columns
                ],
                "foreign_keys": [
                    {
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    }
                    for fk in foreign_keys
                ],
                "indexes": [
                    {
                        "name": idx["name"],
                        "columns": idx["column_names"],
                        "unique": idx["unique"]
                    }
                    for idx in indexes
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get info for table {table_name}",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }