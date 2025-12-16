"""
Marshmallow schemas for eMoney Advisor Service API
Input validation and serialization using Marshmallow
"""
from marshmallow import Schema, fields, validate, ValidationError, post_load
from datetime import datetime
import re

class AuthSchema(Schema):
    """Authentication schema for eMoney Advisor Service - OAuth 2.0 with JWT"""
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
    """Filters schema for eMoney Advisor Service extraction"""
    
    # Date range filter
    dateRange = fields.Nested(DateRangeSchema, allow_none=True)
    
    # Performance tuning
    batchSize = fields.Int(
        validate=validate.Range(min=10, max=100),
        missing=100,
        default=100,
        error_messages={'validator_failed': 'Batch size must be between 10 and 100'}
    )

class ScanConfigSchema(Schema):
    """Scan configuration schema"""
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
            'client',
            'contact',
            'household',
            'spouse',
            'relationship'
        ])),
        required=True,
        validate=validate.Length(min=1),
        error_messages={
            'required': 'Type is required',
            'validator_failed': 'Type must contain at least one valid entity type'
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
    """Schema for querying specific tables"""
    tableName = fields.Str(
        validate=validate.OneOf([
            'client',
            'contact',
            'household',
            'spouse',
            'relationship'
        ]),
        missing='client',
        default='client',
        error_messages={
            'validator_failed': 'Invalid table name. Must be one of: client, contact, household, spouse, relationship'
        }
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