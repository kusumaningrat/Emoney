"""
Marshmallow schemas for eMoney Financial Plan Service API
Input validation and serialization using Marshmallow
"""
from marshmallow import Schema, fields, validate, ValidationError, post_load
from datetime import datetime
import re

class AuthSchema(Schema):
    """Authentication schema for eMoney Financial Plan Service - OAuth 2.0 with JWT"""
    client_id = fields.Str(
        required=True,
        validate=validate.Length(min=5),
        error_messages={'required': 'Client ID is required'}
    )
    
    jwt_token = fields.Str(
        required=True,
        validate=validate.Length(min=10),
        error_messages={'required': 'JWT token is required'}
    )
    
    api_key = fields.Str(
        required=True,
        validate=validate.Length(min=5),
        error_messages={'required': 'API key is required'}
    )
    
    firm_id = fields.Str(required=False, allow_none=True, missing=None)
    scope = fields.Str(required=False, allow_none=True, missing='API')

class DateRangeSchema(Schema):
    """Date range schema"""
    startDate = fields.Str(
        validate=validate.Regexp(
            r'^\d{4}-\d{2}-\d{2}$',
            error='Date must be in YYYY-MM-DD format'
        ),
        allow_none=True
    )
    endDate = fields.Str(
        validate=validate.Regexp(
            r'^\d{4}-\d{2}-\d{2}$',
            error='Date must be in YYYY-MM-DD format'
        ),
        allow_none=True
    )
    
    @post_load
    def validate_date_range(self, data, **kwargs):
        """Validate that start date is before end date"""
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                if start > end:
                    raise ValidationError('Start date must be before end date')
            except ValueError:
                raise ValidationError('Invalid date format')
        
        return data

class FiltersSchema(Schema):
    """Filters schema for eMoney Financial Plan Service extraction"""
    
    # Date range filter
    dateRange = fields.Nested(DateRangeSchema, allow_none=True)
    
    # Include archived plans/goals/scenarios
    includeArchived = fields.Bool(missing=False, default=False)
    
    # Performance tuning
    batchSize = fields.Int(
        validate=validate.Range(min=10, max=1000),
        missing=100,
        default=100,
        error_messages={'validator_failed': 'Batch size must be between 10 and 1000'}
    )

class ScanConfigSchema(Schema):
    """Scan configuration schema for financial plan extraction"""
    scanId = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=255),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error='Scan ID can only contain letters, numbers, underscores, and hyphens'
            )
        ],
        error_messages={'required': 'Scan ID is required'}
    )
    organizationId = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Organization ID is required'}
    )
    type = fields.List(
        fields.Str(validate=validate.OneOf([
            'plan',
            'goal',
            'scenario',
            'cashflow',
            'networth'
        ])),
        required=True,
        validate=validate.Length(min=1),
        error_messages={
            'required': 'Type is required',
            'validator_failed': 'Type must contain at least one valid entity type (plan, goal, scenario, cashflow, networth)'
        }
    )
    auth = fields.Nested(
        AuthSchema,
        required=True,
        error_messages={'required': 'Authentication is required'}
    )
    filters = fields.Nested(FiltersSchema, missing=dict, default=dict)

class ScanRequestSchema(Schema):
    """Complete scan request schema"""
    config = fields.Nested(
        ScanConfigSchema,
        required=True,
        error_messages={'required': 'Config is required'}
    )

class PaginationSchema(Schema):
    """Pagination parameters schema - eMoney uses page & pageSize"""
    page = fields.Int(
        validate=validate.Range(min=1),
        missing=1,
        default=1,
        error_messages={'validator_failed': 'Page must be at least 1'}
    )
    pageSize = fields.Int(
        validate=validate.Range(min=1, max=100),
        missing=100,
        default=100,
        error_messages={'validator_failed': 'Page size must be between 1 and 100'}
    )

class CleanupRequestSchema(Schema):
    """Cleanup request schema"""
    daysOld = fields.Int(
        validate=validate.Range(min=1, max=365),
        missing=7,
        default=7,
        error_messages={
            'validator_failed': 'daysOld must be between 1 and 365 days'
        }
    )

class TableQuerySchema(Schema):
    """Schema for querying specific financial plan tables"""
    tableName = fields.Str(
        validate=validate.OneOf([
            'plan',
            'goal',
            'scenario',
            'cashflow',
            'networth'
        ]),
        missing='plan',
        default='plan',
        error_messages={
            'validator_failed': 'Invalid table name. Must be one of: plan, goal, scenario, cashflow, networth'
        }
    )

class PlanFilterSchema(Schema):
    """Additional filters specific to plan extraction"""
    planId = fields.Str(allow_none=True)
    clientId = fields.Str(allow_none=True)
    planStatus = fields.Str(
        validate=validate.OneOf(['active', 'archived', 'all']),
        missing='active',
        default='active'
    )

class GoalFilterSchema(Schema):
    """Additional filters specific to goal extraction"""
    goalId = fields.Str(allow_none=True)
    planId = fields.Str(allow_none=True)
    goalType = fields.Str(allow_none=True)
    goalStatus = fields.Str(
        validate=validate.OneOf(['active', 'completed', 'archived', 'all']),
        missing='active',
        default='active'
    )

class ScenarioFilterSchema(Schema):
    """Additional filters specific to scenario extraction"""
    scenarioId = fields.Str(allow_none=True)
    planId = fields.Str(allow_none=True)
    scenarioType = fields.Str(allow_none=True)
    includeProjections = fields.Bool(missing=True, default=True)

class CashFlowFilterSchema(Schema):
    """Additional filters specific to cashflow extraction"""
    cashFlowId = fields.Str(allow_none=True)
    scenarioId = fields.Str(allow_none=True)
    planId = fields.Str(allow_none=True)
    yearStart = fields.Int(
        validate=validate.Range(min=1900, max=2100),
        allow_none=True
    )
    yearEnd = fields.Int(
        validate=validate.Range(min=1900, max=2100),
        allow_none=True
    )

class NetWorthFilterSchema(Schema):
    """Additional filters specific to networth extraction"""
    netWorthId = fields.Str(allow_none=True)
    scenarioId = fields.Str(allow_none=True)
    planId = fields.Str(allow_none=True)
    yearStart = fields.Int(
        validate=validate.Range(min=1900, max=2100),
        allow_none=True
    )
    yearEnd = fields.Int(
        validate=validate.Range(min=1900, max=2100),
        allow_none=True
    )

class ScanConfig:
    """Scan configuration data class"""
    def __init__(self, scanId: str, organizationId: str, type: list, auth: dict, filters: dict = None):
        self.scanId = scanId
        self.organizationId = organizationId
        self.type = type
        self.auth = auth
        self.filters = filters or {}

# Schema instances for reuse
scan_config_schema = ScanConfigSchema()
scan_request_schema = ScanRequestSchema()
pagination_schema = PaginationSchema()
cleanup_request_schema = CleanupRequestSchema()
table_query_schema = TableQuerySchema()

# Entity-specific filter schemas
plan_filter_schema = PlanFilterSchema()
goal_filter_schema = GoalFilterSchema()
scenario_filter_schema = ScenarioFilterSchema()
cashflow_filter_schema = CashFlowFilterSchema()
networth_filter_schema = NetWorthFilterSchema()

def validate_scan_request(json_data: dict) -> dict:
    """Validate scan request data and return validated config"""
    try:
        validated = scan_request_schema.load(json_data)
        return validated['config']
    except ValidationError as err:
        raise err

def validate_pagination_params(page, page_size, max_page_size: int = 100) -> tuple:
    """Validate pagination parameters (page/pageSize)"""
    try:
        data = {'page': page, 'pageSize': page_size}
        # Create a temporary schema with custom max page size
        temp_schema = PaginationSchema()
        temp_schema.fields['pageSize'].validate = validate.Range(min=1, max=max_page_size)
        validated = temp_schema.load(data)
        return validated['page'], validated['pageSize']
    except ValidationError as err:
        raise err

def validate_limit_offset_params(limit, offset, max_limit: int = 100) -> tuple:
    """Validate limit/offset pagination parameters"""
    try:
        # Convert to int if they're strings
        limit = int(limit) if limit else max_limit
        offset = int(offset) if offset else 0
        
        # Validate limit
        if limit < 1 or limit > max_limit:
            raise ValidationError({
                'limit': [f'Must be greater than or equal to 1 and less than or equal to {max_limit}.']
            })
        
        # Validate offset
        if offset < 0:
            raise ValidationError({
                'offset': ['Must be greater than or equal to 0.']
            })
        
        return limit, offset
    except (ValueError, TypeError) as e:
        raise ValidationError({
            'pagination': [f'Invalid pagination parameters: {str(e)}']
        })

def validate_cleanup_request(json_data: dict) -> int:
    """Validate cleanup request and return days_old"""
    try:
        validated = cleanup_request_schema.load(json_data)
        return validated['daysOld']
    except ValidationError as err:
        raise err

def validate_table_query(table_name: str) -> str:
    """Validate table name parameter"""
    try:
        validated = table_query_schema.load({'tableName': table_name})
        return validated['tableName']
    except ValidationError as err:
        raise err

def validate_entity_filters(entity_type: str, filters: dict) -> dict:
    """Validate entity-specific filters based on entity type"""
    try:
        if entity_type == 'plan':
            return plan_filter_schema.load(filters)
        elif entity_type == 'goal':
            return goal_filter_schema.load(filters)
        elif entity_type == 'scenario':
            return scenario_filter_schema.load(filters)
        elif entity_type == 'cashflow':
            return cashflow_filter_schema.load(filters)
        elif entity_type == 'networth':
            return networth_filter_schema.load(filters)
        else:
            return filters
    except ValidationError as err:
        raise err

def get_entity_primary_key(entity_type: str) -> str:
    """Get the primary key field name for a given entity type"""
    primary_keys = {
        'plan': 'PlanID',
        'goal': 'GoalID',
        'scenario': 'ScenarioID',
        'cashflow': 'CashFlowID',
        'networth': 'NetWorthID'
    }
    return primary_keys.get(entity_type.lower(), 'id')

def get_valid_entity_types() -> list:
    """Return list of valid entity types"""
    return ['plan', 'goal', 'scenario', 'cashflow', 'networth']