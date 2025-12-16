"""
Swagger/OpenAPI schema definitions for eMoney Identity Service Extraction API
"""
from flask_restx import fields, Api

def register_models(api: Api):
    """Register all API models with the Flask-RESTX Api instance"""
    
    # Authentication model
    auth_model = api.model('Auth', {
        'client_id': fields.String(
            required=True, 
            description='OAuth2 client ID', 
            example='emoney-identity-client-123456789'
        ),
        'client_secret': fields.String(
            required=True, 
            description='OAuth2 client secret', 
            example='c1ient-s3cret-v4lue-example'
        ),
        'grant_type': fields.String(
            required=False,
            description='OAuth2 grant type',
            default='client_credentials',
            example='client_credentials'
        ),
        'scope': fields.String(
            required=False,
            description='OAuth2 scope',
            default='read',
            example='read'
        )
    })

    # Date range model
    date_range_model = api.model('DateRange', {
        'startDate': fields.String(
            description='Start date (YYYY-MM-DD)', 
            example='2025-01-01'
        ),
        'endDate': fields.String(
            description='End date (YYYY-MM-DD)',
            example='2025-12-31'
        )
    })

    # Filters model - simplified
    filters_model = api.model('Filters', {
        'dateRange': fields.Nested(
            date_range_model, 
            description='Date range filter for filtering entities by creation/modification date'
        ),
        'batchSize': fields.Integer(
            description='Batch size for extraction (controls number of records fetched per API call)',
            min=10,
            max=1000,
            default=100,
            example=100
        )
    })

    # Scan configuration model
    scan_config_model = api.model('ScanConfig', {
        'scanId': fields.String(
            required=True, 
            description='Unique identifier for the scan',
            example='emoney-identity-scan-2025-001'
        ),
        'organizationId': fields.String(
            required=True, 
            description='Organization identifier',
            example='org-12345'
        ),
        'type': fields.List(
            fields.String(
                enum=['user', 'office', 'role', 'permission', 'sharingrule', 'logon'],
                description='Type of entity (lowercase with underscore)'
            ), 
            required=True,
            description='Type of entities to extract (must use lowercase format)',
            example=['user']
        ),
        'auth': fields.Nested(auth_model, required=True),
        'filters': fields.Nested(filters_model, description='Optional scan filters')
    })

    # Type to table name mapping model for documentation
    type_mapping_model = api.model('TypeMapping', {
        'user': fields.String(description='Maps to table', example='user'),
        'office': fields.String(description='Maps to table', example='office'),
        'role': fields.String(description='Maps to table', example='role'),
        'permission': fields.String(description='Maps to table', example='permission'),
        'sharingrule': fields.String(description='Maps to table', example='sharingrule'),
        'logon': fields.String(description='Maps to table', example='logon')
    })

    # Table name model - all lowercase
    table_name_model = api.model('TableName', {
        'tableName': fields.String(
            enum=['user', 'office', 'role', 'permission', 'sharingrule', 'logon'],
            description='Table name for data retrieval (lowercase)',
            example='user'
        )
    })

    # Scan request model
    scan_request_model = api.model('ScanRequest', {
        'config': fields.Nested(scan_config_model, required=True)
    })

    # Checkpoint info model
    checkpoint_info_model = api.model('CheckpointInfo', {
        'latestCheckpoint': fields.Raw(description='Latest checkpoint data'),
        'progress': fields.Float(description='Progress percentage if available'),
        'lastCheckpointAt': fields.String(description='When last checkpoint was created'),
        'entity': fields.String(description='Current entity being processed'),
        'phase': fields.String(description='Current extraction phase')
    })

    # Scan status model
    scan_status_model = api.model('ScanStatus', {
        'scanId': fields.String(description='Scan identifier'),
        'organizationId': fields.String(description='Organization identifier'),
        'type': fields.List(fields.String, description='Scan types (lowercase with underscore)'),
        'status': fields.String(
            description='Scan status', 
            enum=['pending', 'running', 'completed', 'failed', 'cancelled', 'paused', 'crashed', 'resuming']
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

    # Entity field model
    entity_field_model = api.model('EntityField', {
        'name': fields.String(description='Field name'),
        'type': fields.String(description='Field type'),
        'description': fields.String(description='Field description'),
        'required': fields.Boolean(description='Whether field is required')
    })

    # Entity schema model
    entity_schema_model = api.model('EntitySchema', {
        'entity': fields.String(description='Entity type'),
        'fields': fields.List(fields.Nested(entity_field_model)),
        'filters': fields.Raw(description='Available filters')
    })

    # Table info model
    table_info_model = api.model('TableInfo', {
        'name': fields.String(
            description='Table name (lowercase: user, office, role, permission, sharingrule, logon)',
            example='user'
        ),
        'rowCount': fields.Integer(description='Current row count in database'),
        'extractedCount': fields.Integer(description='Number of records extracted during scan'),
        'entityType': fields.String(description='Corresponding entity type (lowercase)')
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
        'tableName': fields.String(
            description='Table name (lowercase: user, office, role, permission, sharingrule, logon)',
            enum=['user', 'office', 'role', 'permission', 'sharingrule', 'logon'],
            example='user'
        ),
        'records': fields.List(fields.Raw, description='Array of data records'),
        'pagination': fields.Nested(pagination_model),
        'availableTables': fields.List(
            fields.String(
                enum=['user', 'office', 'role', 'permission', 'sharingrule', 'logon'],
                description='Available table names (lowercase)'
            ),
            description='Available table names'
        ),
        'columns': fields.List(fields.String, description='Column names in the table')
    })

    # Pipeline info model
    pipeline_info_model = api.model('PipelineInfo', {
        'pipeline_name': fields.String(description='Pipeline name'),
        'destination_type': fields.String(description='Destination type'),
        'working_dir': fields.String(description='Working directory'),
        'dataset_name': fields.String(description='Dataset name'),
        'is_active': fields.Boolean(description='Whether pipeline is active'),
        'source_type': fields.String(description='Source type'),
        'uses_api_service': fields.Boolean(description='Whether using API service'),
        'configuration_method': fields.String(description='Configuration method'),
        'database_health': fields.Boolean(description='Database health status'),
        'supports_checkpoints': fields.Boolean(description='Whether checkpoints are supported'),
        'error': fields.String(description='Error message if any')
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

    # Health model
    health_model = api.model('Health', {
        'status': fields.String(description='Service status', enum=['healthy', 'degraded', 'unhealthy']),
        'timestamp': fields.String(description='Timestamp'),
        'service': fields.String(description='Service name'),
        'environment': fields.String(description='Environment (development, staging, production)'),
        'version': fields.String(description='API version'),
        'pipeline': fields.Nested(pipeline_info_model, description='Pipeline information'),
        'database_health': fields.Raw(description='Detailed database health information'),
        'database_info': fields.Raw(description='Database connection information'),
        'config': fields.Raw(description='Service configuration summary'),
        'issues': fields.List(fields.String, description='List of current issues'),
        'error': fields.String(description='Error message if unhealthy')
    })

    # Statistics model
    statistics_model = api.model('Statistics', {
        'total_jobs': fields.Integer(description='Total number of jobs'),
        'status_breakdown': fields.Raw(description='Job count by status'),
        'recent_jobs_7_days': fields.Integer(description='Recent jobs in last 7 days'),
        'total_records_extracted': fields.Integer(description='Total records extracted across all jobs'),
        'organization_filter': fields.String(description='Organization filter applied'),
        'entity_breakdown': fields.Raw(description='Records by entity type'),
        'generated_at': fields.String(description='When statistics were generated')
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
        'entity_field_model': entity_field_model,
        'entity_schema_model': entity_schema_model,
        'table_info_model': table_info_model,
        'tables_response_model': tables_response_model,
        'results_response_model': results_response_model,
        'pipeline_info_model': pipeline_info_model,
        'cleanup_request_model': cleanup_request_model,
        'cleanup_response_model': cleanup_response_model,
        'api_response_model': api_response_model,
        'health_model': health_model,
        'statistics_model': statistics_model,
        'type_mapping_model': type_mapping_model,
        'table_name_model': table_name_model
    }