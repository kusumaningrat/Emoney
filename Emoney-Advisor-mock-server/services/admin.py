# services/admin.py

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from database import Base, engine
from typing import Dict, Any, Optional
from datetime import datetime

# Import seeders
from seeders.identity_seeder import IdentitySeeder
from seeders.client_seeder import ClientSeeder
from seeders.financial_seeder import FinancialSeeder
from seeders.account_seeder import AccountSeeder
from seeders.asset_seeder import AssetSeeder

# Import all models to ensure they're registered with Base
# V1 - Identity & Access Management
from models.identity import (
    User, Office, Role, Permission, SharingRule, Logon
)

# V2 - Client & Household Management
from models.client import (
    Client, Household, Spouse, Contact, Relationship
)

# V3 - Financial Planning Core
from models.financial import (
    FinancialPlan, Goal, Scenario, CashFlow, NetWorth
)

# V4 - Account & Asset Management
from models.account import Account, AccountType
from models.asset import Asset, AssetClass, Liability


class AdminService:
    def __init__(self, db: Session):
        self.db = db
    
    def seed_database(self, entity_type: str = "all") -> Dict[str, Any]:
        """
        Seed the database with test data based on entity_type.
        
        Args:
            entity_type: Type of entities to seed ("all", "identity", "clients", "financial", "accounts", "assets")
        
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
            
            if entity_type in ["all", "clients"]:
                print("Seeding Client (V2) data...")
                client_seeder = ClientSeeder(self.db)
                client_data = client_seeder.seed_all()
                
                results["seeded_entities"]["clients"] = {
                    "households": len(client_data.get("households", [])),
                    "clients": len(client_data.get("clients", [])),
                    "spouses": len(client_data.get("spouses", [])),
                    "contacts": len(client_data.get("contacts", [])),
                    "relationships": len(client_data.get("relationships", []))
                }
            
            if entity_type in ["all", "financial"]:
                print("Seeding Financial (V3) data...")
                financial_seeder = FinancialSeeder(self.db)
                financial_data = financial_seeder.seed_all()
                
                results["seeded_entities"]["financial"] = {
                    "financial_plans": len(financial_data.get("financial_plans", [])),
                    "goals": len(financial_data.get("goals", [])),
                    "scenarios": len(financial_data.get("scenarios", [])),
                    "cash_flows": len(financial_data.get("cash_flows", [])),
                    "net_worths": len(financial_data.get("net_worths", []))
                }
            
            if entity_type in ["all", "accounts"]:
                print("Seeding Account (V4) data...")
                account_seeder = AccountSeeder(self.db)
                account_data = account_seeder.seed_all()
                
                results["seeded_entities"]["accounts"] = {
                    "account_types": len(account_data.get("account_types", [])),
                    "accounts": len(account_data.get("accounts", []))
                }
            
            if entity_type in ["all", "assets"]:
                print("Seeding Asset (V4) data...")
                asset_seeder = AssetSeeder(self.db)
                asset_data = asset_seeder.seed_all()
                
                results["seeded_entities"]["assets"] = {
                    "asset_classes": len(asset_data.get("asset_classes", [])),
                    "assets": len(asset_data.get("assets", [])),
                    "liabilities": len(asset_data.get("liabilities", []))
                }
            
            return results
            
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "entity_type": entity_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def seed_version(self, version: str) -> Dict[str, Any]:
        """
        Seed data for a specific version.
        
        Args:
            version: Version to seed ("v1", "v2", "v3", "v4", "all")
        
        Returns:
            Dictionary with seeding results
        """
        version_mapping = {
            "v1": "identity",
            "v2": "clients", 
            "v3": "financial",
            "v4": ["accounts", "assets"]
        }
        
        if version == "all":
            return self.seed_database("all")
        elif version == "v4":
            # V4 includes both accounts and assets
            accounts_result = self.seed_database("accounts")
            assets_result = self.seed_database("assets")
            
            return {
                "status": "success",
                "version": version,
                "seeded_entities": {
                    **accounts_result.get("seeded_entities", {}),
                    **assets_result.get("seeded_entities", {})
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        elif version in version_mapping:
            entity_type = version_mapping[version]
            return self.seed_database(entity_type)
        else:
            return {
                "status": "error",
                "message": f"Invalid version: {version}. Valid versions: v1, v2, v3, v4, all",
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
            
            # For PostgreSQL: Handle foreign key dependencies with CASCADE
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                # Drop all tables individually with CASCADE for PostgreSQL
                for table in existing_tables:
                    try:
                        self.db.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    except Exception as e:
                        print(f"Warning: Could not drop table {table}: {str(e)}")
                
                self.db.commit()
            
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
            version_tables = {
                "v1_identity": [
                    "users", "offices", "roles", "permissions",
                    "user_roles", "role_permissions", "sharing_rules", "logons"
                ],
                "v2_clients": [
                    "clients", "contacts", "households", "spouses", "relationships"
                ],
                "v3_financial": [
                    "financial_plans", "goals", "scenarios", "cash_flows", "net_worths"
                ],
                "v4_accounts_assets": [
                    "account_types", "accounts", "asset_classes", "assets", "liabilities"
                ]
            }
            
            def sum_counts(table_list):
                return sum(
                    table_counts.get(table, 0) 
                    for table in table_list 
                    if isinstance(table_counts.get(table), int)
                )
            
            version_counts = {}
            for version, table_list in version_tables.items():
                version_counts[version] = sum_counts(table_list)
            
            return {
                "status": "success",
                "database": {
                    "total_tables": len(tables),
                    "tables": sorted(tables)
                },
                "record_counts": {
                    "by_table": table_counts,
                    "by_version": {
                        **version_counts,
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
    
    def verify_seeding(self, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify that seeding was successful by checking expected counts.
        
        Args:
            version: Specific version to verify ("v1", "v2", "v3", "v4") or None for all
        
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
                # V2 - Client & Household Management
                "clients": 250,
                "households": 150,
                "spouses": 180,
                "contacts": 100,
                "relationships": 120,
                # V3 - Financial Planning Core
                "financial_plans": 200,
                "goals": 800,
                "scenarios": 150,
                "cash_flows": 200,
                "net_worths": 200,
                # V4 - Account & Asset Management
                "account_types": 15,
                "accounts": 500,
                "asset_classes": 12,
                "assets": 800,
                "liabilities": 300
            }
            
            # Filter by version if specified
            if version:
                version_tables = {
                    "v1": ["users", "offices", "roles", "permissions", "sharing_rules", "logons"],
                    "v2": ["clients", "households", "spouses", "contacts", "relationships"],
                    "v3": ["financial_plans", "goals", "scenarios", "cash_flows", "net_worths"],
                    "v4": ["account_types", "accounts", "asset_classes", "assets", "liabilities"]
                }
                if version in version_tables:
                    expected_counts = {
                        table: expected_counts[table] 
                        for table in version_tables[version] 
                        if table in expected_counts
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
                        "passed": passed,
                        "difference": actual - expected
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
                "version": version or "all",
                "verification": verification_results,
                "summary": {
                    "total_checks": len(verification_results),
                    "passed": sum(1 for v in verification_results.values() if v.get("passed", False)),
                    "failed": sum(1 for v in verification_results.values() if not v.get("passed", False))
                },
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
            
            # Disable foreign key checks temporarily
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
    
    def truncate_version_tables(self, version: str) -> Dict[str, Any]:
        """
        Truncate tables for a specific version only.
        
        Args:
            version: Version to truncate ("v1", "v2", "v3", "v4")
        
        Returns:
            Dictionary with truncation results
        """
        try:
            version_tables = {
                "v1": ["logons", "sharing_rules", "user_roles", "role_permissions", "users", "offices", "roles", "permissions"],
                "v2": ["relationships", "contacts", "spouses", "clients", "households"],
                "v3": ["cash_flows", "net_worths", "scenarios", "goals", "financial_plans"],
                "v4": ["assets", "liabilities", "accounts", "account_types", "asset_classes"]
            }
            
            if version not in version_tables:
                return {
                    "status": "error",
                    "message": f"Invalid version: {version}. Valid versions: v1, v2, v3, v4",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tables_to_truncate = version_tables[version]
            
            # Disable foreign key checks temporarily
            try:
                self.db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            except:
                try:
                    self.db.execute(text("SET session_replication_role = 'replica'"))
                except:
                    self.db.execute(text("PRAGMA foreign_keys = OFF"))
            
            truncated_tables = []
            for table in tables_to_truncate:
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
                "message": f"Version {version} tables truncated successfully",
                "version": version,
                "truncated_tables": len(truncated_tables),
                "tables": truncated_tables,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "status": "error",
                "message": f"Failed to truncate {version} tables",
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
            
            # Check if table exists
            tables = inspector.get_table_names()
            if table_name not in tables:
                return {
                    "status": "error",
                    "message": f"Table '{table_name}' not found",
                    "available_tables": sorted(tables),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
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
                        "default": col.get("default"),
                        "primary_key": col.get("primary_key", False)
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
    
    def get_version_summary(self) -> Dict[str, Any]:
        """
        Get summary of implementation status for all versions.
        
        Returns:
            Dictionary with version implementation summary
        """
        try:
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names())
            
            version_info = {
                "v1": {
                    "name": "Identity & Access Management",
                    "expected_tables": ["users", "offices", "roles", "permissions", "user_roles", "role_permissions", "sharing_rules", "logons"],
                    "expected_records": {"users": 60, "offices": 15, "roles": 10, "permissions": 50, "sharing_rules": 80, "logons": 100}
                },
                "v2": {
                    "name": "Client & Household Management", 
                    "expected_tables": ["clients", "households", "spouses", "contacts", "relationships"],
                    "expected_records": {"clients": 250, "households": 150, "spouses": 180, "contacts": 100, "relationships": 120}
                },
                "v3": {
                    "name": "Financial Planning Core",
                    "expected_tables": ["financial_plans", "goals", "scenarios", "cash_flows", "net_worths"],
                    "expected_records": {"financial_plans": 200, "goals": 800, "scenarios": 150, "cash_flows": 200, "net_worths": 200}
                },
                "v4": {
                    "name": "Account & Asset Management",
                    "expected_tables": ["account_types", "accounts", "asset_classes", "assets", "liabilities"],
                    "expected_records": {"account_types": 15, "accounts": 500, "asset_classes": 12, "assets": 800, "liabilities": 300}
                }
            }
            
            summary = {}
            
            for version, info in version_info.items():
                expected_tables = set(info["expected_tables"])
                existing_version_tables = expected_tables.intersection(existing_tables)
                
                # Get record counts for existing tables
                record_counts = {}
                total_records = 0
                for table in existing_version_tables:
                    try:
                        result = self.db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        record_counts[table] = count
                        total_records += count
                    except Exception:
                        record_counts[table] = 0
                
                summary[version] = {
                    "name": info["name"],
                    "status": "Complete" if existing_version_tables == expected_tables else "Incomplete",
                    "tables_implemented": len(existing_version_tables),
                    "tables_expected": len(expected_tables),
                    "missing_tables": list(expected_tables - existing_version_tables),
                    "total_records": total_records,
                    "record_counts": record_counts,
                    "expected_total": sum(info["expected_records"].values())
                }
            
            return {
                "status": "success",
                "summary": summary,
                "overall": {
                    "total_versions": len(version_info),
                    "complete_versions": sum(1 for v in summary.values() if v["status"] == "Complete"),
                    "total_tables": len(existing_tables),
                    "total_records": sum(v["total_records"] for v in summary.values())
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": "Failed to get version summary",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }