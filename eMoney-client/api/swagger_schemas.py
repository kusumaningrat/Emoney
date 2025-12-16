"""
Swagger/OpenAPI schema definitions for eMoney Extraction API
"""
from flask_restx import fields, Api

def register_models(api: Api):
    """Register all API models with the Flask-RESTX Api instance"""
    
    # Authentication model - eMoney OAuth2/JWT
    auth_model = api.model('Auth', {
        'client_id': fields.String(
            required=True, 
            description='eMoney Client ID', 
            example='emoney-client-id-12345'
        ),
        'jwt_token': fields.String(
            required=True, 
            description='eMoney JWT token', 
            example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
        ),
        'api_key': fields.String(
            required=True,
            description='eMoney API key',
            example='emoney-api-key-67890'
        ),
        'firm_id': fields.String(
            required=False, 
            description='Optional firm identifier', 
            example='firm-12345'
        ),
        'scope': fields.String(
            required=False,
            description='Optional API scope',
            example='API',
            default='API'
        )
    })

    # Date range model
    date_range_model = api.model('DateRange', {
        'startDate': fields.String(
            description='Start date (YYYY-MM-DD)', 
            example='2024-01-01'
        ),
        'endDate': fields.String(
            description='End date (YYYY-MM-DD)',
            example='2024-12-31'
        )
    })

    # Filters model (eMoney only allows dateRange and batchSize)
    filters_model = api.model('Filters', {
        'dateRange': fields.Nested(date_range_model, description='Date range filter'),
        'batchSize': fields.Integer(
            description='Batch size for extraction',
            default=100,
            example=100
        )
    })

    # Scan configuration model
    scan_config_model = api.model('ScanConfig', {
        'scanId': fields.String(
            required=True, 
            description='Unique identifier for the scan',
            example='emoney-scan-2025-001'
        ),
        'organizationId': fields.String(
            required=True, 
            description='Organization identifier',
            example='org-12345'
        ),
        'type': fields.List(
            fields.String, 
            required=True,
            description='Type of scan (client, contact, household, spouse, or relationship)',
            example=['client']
        ),
        'auth': fields.Nested(auth_model, required=True),
        'filters': fields.Nested(filters_model, description='Scan filters')
    })

    # Scan request model
    scan_request_model = api.model('ScanRequest', {
        'config': fields.Nested(scan_config_model, required=True)
    })

    # Checkpoint info model
    checkpoint_info_model = api.model('CheckpointInfo', {
        'latestCheckpoint': fields.Raw(description='Latest checkpoint data'),
        'progress': fields.Float(description='Progress percentage if available'),
        'lastCheckpointAt': fields.String(description='When last checkpoint was created')
    })

    # Scan status model
    scan_status_model = api.model('ScanStatus', {
        'scanId': fields.String(description='Scan identifier'),
        'organizationId': fields.String(description='Organization identifier'),
        'type': fields.String(description='Scan type'),
        'status': fields.String(
            description='Scan status', 
            enum=['pending', 'running', 'completed', 'failed', 'cancelled', 'crashed', 'resuming']
        ),
        'startTime': fields.String(description='Scan start time (ISO format)'),
        'endTime': fields.String(description='Scan end time (ISO format)'),
        'lastHeartbeat': fields.String(description='Last heartbeat timestamp'),
        'recordsExtracted': fields.Integer(description='Number of records extracted'),
        'duration': fields.Float(description='Scan duration in seconds'),
        'errorMessage': fields.String(description='Error message if failed'),
        'metadata': fields.Raw(description='Additional scan metadata'),
        'config': fields.Raw(description='Scan configuration'),
        'checkpointInfo': fields.Nested(checkpoint_info_model, description='Checkpoint information if available')
    })

    # Pagination model
    pagination_model = api.model('Pagination', {
        'total': fields.Integer(description='Total number of items'),
        'limit': fields.Integer(description='Items per page'),
        'offset': fields.Integer(description='Offset from start'),
        'hasMore': fields.Boolean(description='Whether more items exist'),
        'totalPages': fields.Integer(description='Total number of pages'),
        'returned': fields.Integer(description='Number of items returned in this response')
    })

    # Scan list model
    scan_list_model = api.model('ScanList', {
        'scans': fields.List(fields.Nested(scan_status_model)),
        'pagination': fields.Nested(pagination_model)
    })

    # Entity property model
    entity_property_model = api.model('EntityProperty', {
        'name': fields.String(description='Property name'),
        'label': fields.String(description='Property label'),
        'type': fields.String(description='Property type'),
        'description': fields.String(description='Property description')
    })

    # Entity properties model
    entity_properties_model = api.model('EntityProperties', {
        'standard': fields.List(fields.Nested(entity_property_model)),
        'filters': fields.Raw(description='Available filters')
    })

    # Table info model
    table_info_model = api.model('TableInfo', {
        'name': fields.String(description='Table name'),
        'rowCount': fields.Integer(description='Current row count in database'),
        'extractedCount': fields.Integer(description='Number of records extracted during scan')
    })

    # Tables response model
    tables_response_model = api.model('TablesResponse', {
        'scanId': fields.String(description='Scan identifier'),
        'datasetName': fields.String(description='Database dataset name'),
        'tables': fields.List(fields.Nested(table_info_model)),
        'totalTables': fields.Integer(description='Total number of tables')
    })

    # Results response model
    results_response_model = api.model('ResultsResponse', {
        'scanId': fields.String(description='Scan identifier'),
        'tableName': fields.String(description='Table name'),
        'records': fields.List(fields.Raw, description='Array of data records'),
        'pagination': fields.Nested(pagination_model),
        'availableTables': fields.List(fields.String, description='Available table names'),
        'columns': fields.List(fields.String, description='Column names in the table')
    })

    # Cleanup request model
    cleanup_request_model = api.model('CleanupRequest', {
        'daysOld': fields.Integer(
            description='Remove scans older than this many days',
            default=7,
            min=1,
            max=365,
            example=7
        )
    })

    # Cleanup response model
    cleanup_response_model = api.model('CleanupResponse', {
        'cleanedCount': fields.Integer(description='Number of scans cleaned up'),
        'daysOld': fields.Integer(description='Days old threshold used')
    })

    # Generic API response model
    api_response_model = api.model('APIResponse', {
        'success': fields.Boolean(description='Whether the request was successful'),
        'message': fields.String(description='Response message'),
        'error': fields.String(description='Error message if failed'),
        'data': fields.Raw(description='Response data')
    })

    # Return models for use in routes
    return {
        'auth_model': auth_model,
        'date_range_model': date_range_model,
        'filters_model': filters_model,
        'scan_config_model': scan_config_model,
        'scan_request_model': scan_request_model,
        'scan_status_model': scan_status_model,
        'checkpoint_info_model': checkpoint_info_model,
        'pagination_model': pagination_model,
        'scan_list_model': scan_list_model,
        'entity_property_model': entity_property_model,
        'entity_properties_model': entity_properties_model,
        'table_info_model': table_info_model,
        'tables_response_model': tables_response_model,
        'results_response_model': results_response_model,
        'cleanup_request_model': cleanup_request_model,
        'cleanup_response_model': cleanup_response_model,
        'api_response_model': api_response_model
    }
