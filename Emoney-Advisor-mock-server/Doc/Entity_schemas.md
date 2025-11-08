eMoney Advisor Entity Schema Categories
Below are the main categories of eMoney Advisor schemas:


User & Access Management Service Schemas
Client & Relationship Management Service Schemas
Financial Planning Service Schemas
Account Management Service Schemas
Asset Management Service Schemas
Document Management Service Schemas
Calendar & Event Service Schemas

eMoney Advisor JSON Schemas by Service
1. User & Access Management Service Schemas
User Schema
json{
  "table": "users",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "firm_id": {
      "type": "string",
      "foreign_key": {
        "table": "firms",
        "column": "id"
      }
    },
    "workspace_id": {
      "type": "string",
      "foreign_key": {
        "table": "workspaces",
        "column": "id"
      },
      "nullable": true
    },
    "username": {
      "type": "string",
      "unique": true,
      "required": true
    },
    "email": {
      "type": "string",
      "unique": true,
      "required": true
    },
    "first_name": {
      "type": "string",
      "required": true
    },
    "last_name": {
      "type": "string",
      "required": true
    },
    "title": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "is_active": {
      "type": "boolean",
      "default": true
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Role Schema
json{
  "table": "roles",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "name": {
      "type": "string",
      "unique": true,
      "required": true
    },
    "description": {
      "type": "string"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Permission Schema
json{
  "table": "permissions",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "role_id": {
      "type": "string",
      "foreign_key": {
        "table": "roles",
        "column": "id"
      }
    },
    "resource": {
      "type": "string",
      "required": true
    },
    "action": {
      "type": "string",
      "required": true
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Firm Schema
json{
  "table": "firms",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "name": {
      "type": "string",
      "required": true
    },
    "address": {
      "type": "string"
    },
    "city": {
      "type": "string"
    },
    "state": {
      "type": "string"
    },
    "postal_code": {
      "type": "string"
    },
    "country": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "email": {
      "type": "string"
    },
    "website": {
      "type": "string"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Advisor Schema
json{
  "table": "advisors",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "user_id": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "firm_id": {
      "type": "string",
      "foreign_key": {
        "table": "firms",
        "column": "id"
      },
      "nullable": true
    },
    "title": {
      "type": "string",
      "required": true
    },
    "specialties": {
      "type": "json"
    },
    "credentials": {
      "type": "json"
    },
    "experience_years": {
      "type": "integer"
    },
    "client_count": {
      "type": "integer"
    },
    "aum": {
      "type": "integer"
    },
    "service_model": {
      "type": "string"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Workspace Schema
json{
  "table": "workspaces",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "name": {
      "type": "string",
      "required": true
    },
    "plan": {
      "type": "string",
      "required": true
    },
    "status": {
      "type": "string",
      "default": "Active",
      "required": true
    },
    "users_limit": {
      "type": "integer"
    },
    "storage_limit": {
      "type": "integer"
    },
    "storage_used": {
      "type": "integer",
      "default": 0
    },
    "custom_domain": {
      "type": "string"
    },
    "features": {
      "type": "json"
    },
    "branding": {
      "type": "json"
    },
    "subscription": {
      "type": "json"
    },
    "settings": {
      "type": "json"
    },
    "api_keys": {
      "type": "json"
    },
    "security": {
      "type": "json"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Logon Schema
json{
  "table": "logons",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "user_id": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "username": {
      "type": "string",
      "unique": true,
      "required": true
    },
    "status": {
      "type": "string",
      "required": true
    },
    "last_login": {
      "type": "datetime"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
2. Client & Relationship Management Service Schemas
Client Schema
json{
  "table": "clients",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "firm_id": {
      "type": "string",
      "foreign_key": {
        "table": "firms",
        "column": "id"
      }
    },
    "first_name": {
      "type": "string",
      "required": true
    },
    "last_name": {
      "type": "string",
      "required": true
    },
    "email": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "marital_status": {
      "type": "string",
      "required": true
    },
    "previous_marriages": {
      "type": "boolean",
      "default": false
    },
    "date_of_birth": {
      "type": "date",
      "required": true
    },
    "owning_advisor": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "external_id": {
      "type": "string"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Spouse Schema
json{
  "table": "spouses",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      },
      "unique": true
    },
    "first_name": {
      "type": "string",
      "required": true
    },
    "last_name": {
      "type": "string",
      "required": true
    },
    "email": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "date_of_birth": {
      "type": "date",
      "required": true
    },
    "previous_marriages": {
      "type": "boolean",
      "default": false
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Household Schema
json{
  "table": "households",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "name": {
      "type": "string",
      "required": true
    },
    "primary_client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "assigned_to": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "status": {
      "type": "string",
      "default": "Active"
    },
    "address": {
      "type": "json"
    },
    "total_aum": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "annual_revenue": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "client_since": {
      "type": "date"
    },
    "servicing_model": {
      "type": "string"
    },
    "review_frequency": {
      "type": "string"
    },
    "next_review_date": {
      "type": "date"
    },
    "primary_advisor": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "secondary_advisor": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      },
      "nullable": true
    },
    "service_team": {
      "type": "json"
    },
    "accounts": {
      "type": "json"
    },
    "goals": {
      "type": "json"
    },
    "financial_plan": {
      "type": "string",
      "nullable": true
    },
    "notes": {
      "type": "string",
      "nullable": true
    },
    "tags": {
      "type": "json"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
HouseholdMember Schema
json{
  "table": "household_members",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "household_id": {
      "type": "string",
      "foreign_key": {
        "table": "households",
        "column": "id"
      }
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      },
      "nullable": true
    },
    "first_name": {
      "type": "string",
      "required": true
    },
    "last_name": {
      "type": "string",
      "required": true
    },
    "relationship": {
      "type": "string",
      "required": true
    },
    "date_of_birth": {
      "type": "date"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Contact Schema
json{
  "table": "contacts",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "type": {
      "type": "string",
      "required": true
    },
    "address_line1": {
      "type": "string"
    },
    "address_line2": {
      "type": "string"
    },
    "city": {
      "type": "string"
    },
    "state": {
      "type": "string"
    },
    "postal_code": {
      "type": "string"
    },
    "country": {
      "type": "string"
    },
    "email": {
      "type": "string"
    },
    "phone": {
      "type": "string"
    },
    "is_preferred": {
      "type": "boolean",
      "default": false
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Relationship Schema
json{
  "table": "relationships",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "related_client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "relationship_type": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "string"
    },
    "notes": {
      "type": "string"
    },
    "start_date": {
      "type": "date"
    },
    "end_date": {
      "type": "date"
    },
    "is_active": {
      "type": "boolean",
      "default": true
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
3. Financial Planning Service Schemas
FinancialPlan Schema
json{
  "table": "financial_plans",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "default": "Active"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Goal Schema
json{
  "table": "goals",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "plan_id": {
      "type": "string",
      "foreign_key": {
        "table": "financial_plans",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "goal_type": {
      "type": "string"
    },
    "target_date": {
      "type": "date"
    },
    "target_amount": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "priority": {
      "type": "string"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
MonteCarlo Schema
json{
  "table": "monte_carlos",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "plan_id": {
      "type": "string",
      "foreign_key": {
        "table": "financial_plans",
        "column": "id"
      }
    },
    "success_rate": {
      "type": "decimal",
      "precision": 5,
      "scale": 2
    },
    "iterations": {
      "type": "integer"
    },
    "simulation_date": {
      "type": "date"
    },
    "parameters": {
      "type": "json"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
CashFlow Schema
json{
  "table": "cash_flows",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "plan_id": {
      "type": "string",
      "foreign_key": {
        "table": "financial_plans",
        "column": "id"
      }
    },
    "year": {
      "type": "integer",
      "required": true
    },
    "income": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "expenses": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "net_flow": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
4. Account Management Service Schemas
Account Schema
json{
  "table": "accounts",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "account_type": {
      "type": "string",
      "required": true
    },
    "balance": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "institution": {
      "type": "string"
    },
    "account_number": {
      "type": "string"
    },
    "is_taxable": {
      "type": "boolean",
      "default": false
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Investment Schema
json{
  "table": "investments",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "account_id": {
      "type": "string",
      "foreign_key": {
        "table": "accounts",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "symbol": {
      "type": "string"
    },
    "shares": {
      "type": "decimal",
      "precision": 15,
      "scale": 6
    },
    "price": {
      "type": "decimal",
      "precision": 15,
      "scale": 6
    },
    "value": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "as_of_date": {
      "type": "date"
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Liability Schema
json{
  "table": "liabilities",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "liability_type": {
      "type": "string",
      "required": true
    },
    "balance": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "interest_rate": {
      "type": "decimal",
      "precision": 5,
      "scale": 2
    },
    "monthly_payment": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "start_date": {
      "type": "date"
    },
    "end_date": {
      "type": "date"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
5. Asset Management Service Schemas
Asset Schema
json{
  "table": "assets",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "asset_type": {
      "type": "string",
      "required": true
    },
    "value": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "basis": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "acquisition_date": {
      "type": "date"
    },
    "growth_rate": {
      "type": "decimal",
      "precision": 5,
      "scale": 2
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Income Schema
json{
  "table": "incomes",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "income_type": {
      "type": "string",
      "required": true
    },
    "amount": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "frequency": {
      "type": "string",
      "required": true
    },
    "start_date": {
      "type": "date"
    },
    "end_date": {
      "type": "date"
    },
    "growth_rate": {
      "type": "decimal",
      "precision": 5,
      "scale": 2
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Expense Schema
json{
  "table": "expenses",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "expense_type": {
      "type": "string",
      "required": true
    },
    "amount": {
      "type": "decimal",
      "precision": 15,
      "scale": 2
    },
    "frequency": {
      "type": "string",
      "required": true
    },
    "start_date": {
      "type": "date"
    },
    "end_date": {
      "type": "date"
    },
    "inflation_rate": {
      "type": "decimal",
      "precision": 5,
      "scale": 2
    },
    "is_goal": {
      "type": "boolean",
      "default": false
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
6. Document Management Service Schemas
Document Schema
json{
  "table": "documents",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "name": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "string"
    },
    "document_type": {
      "type": "string",
      "required": true
    },
    "file_path": {
      "type": "string",
      "required": true
    },
    "file_size": {
      "type": "integer"
    },
    "mime_type": {
      "type": "string"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Note Schema
json{
  "table": "notes",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "title": {
      "type": "string",
      "required": true
    },
    "content": {
      "type": "text",
      "required": true
    },
    "note_type": {
      "type": "string"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Task Schema
json{
  "table": "tasks",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "client_id": {
      "type": "string",
      "foreign_key": {
        "table": "clients",
        "column": "id"
      }
    },
    "title": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "text"
    },
    "due_date": {
      "type": "date"
    },
    "status": {
      "type": "string",
      "default": "Open"
    },
    "priority": {
      "type": "string"
    },
    "assigned_to": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
7. Calendar & Event Service Schemas
Calendar Schema
json{
  "table": "calendars",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "user_id": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      },
      "required": true
    },
    "name": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "string"
    },
    "color": {
      "type": "string"
    },
    "is_primary": {
      "type": "boolean",
      "default": false
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}
Event Schema
json{
  "table": "events",
  "primary_key": "id",
  "schema": {
    "id": {
      "type": "string",
      "primary_key": true
    },
    "calendar_id": {
      "type": "string",
      "foreign_key": {
        "table": "calendars",
        "column": "id"
      }
    },
    "title": {
      "type": "string",
      "required": true
    },
    "description": {
      "type": "text"
    },
    "location": {
      "type": "string"
    },
    "start_time": {
      "type": "datetime",
      "required": true
    },
    "end_time": {
      "type": "datetime",
      "required": true
    },
    "all_day": {
      "type": "boolean",
      "default": false
    },
    "recurrence": {
      "type": "json"
    },
    "attendees": {
      "type": "json"
    },
    "created_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "updated_by": {
      "type": "string",
      "foreign_key": {
        "table": "users",
        "column": "id"
      }
    },
    "created_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    },
    "updated_at": {
      "type": "datetime",
      "default": "CURRENT_TIMESTAMP"
    }
  }
}