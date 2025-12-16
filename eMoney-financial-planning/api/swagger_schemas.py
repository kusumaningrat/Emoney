"""
Swagger/OpenAPI schema definitions for eMoney Financial Plan Extraction API
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
            example='2025-01-01'
        ),
        'endDate': fields.String(
            description='End date (YYYY-MM-DD)',
            example='2025-12-31'
        )
    })

    # Filters model for financial plan extraction
    filters_model = api.model('Filters', {
        'dateRange': fields.Nested(date_range_model, description='Date range filter'),
        'includeArchived': fields.Boolean(
            description='Include archived plans/goals/scenarios',
            default=False,
            example=False
        ),
        'batchSize': fields.Integer(
            description='Batch size for extraction',
            default=100,
            example=100,
            min=10,
            max=1000
        )
    })

    # Plan-specific filters
    plan_filters_model = api.model('PlanFilters', {
        'planId': fields.String(description='Specific plan ID to extract', example='PLAN123'),
        'clientId': fields.String(description='Filter by client ID', example='CLIENT456'),
        'planStatus': fields.String(
            description='Plan status filter',
            enum=['active', 'archived', 'all'],
            default='active',
            example='active'
        )
    })

    # Goal-specific filters
    goal_filters_model = api.model('GoalFilters', {
        'goalId': fields.String(description='Specific goal ID to extract', example='GOAL789'),
        'planId': fields.String(description='Filter by plan ID', example='PLAN123'),
        'goalType': fields.String(description='Goal type filter', example='retirement'),
        'goalStatus': fields.String(
            description='Goal status filter',
            enum=['active', 'completed', 'archived', 'all'],
            default='active',
            example='active'
        )
    })

    # Scenario-specific filters
    scenario_filters_model = api.model('ScenarioFilters', {
        'scenarioId': fields.String(description='Specific scenario ID to extract', example='SCENARIO001'),
        'planId': fields.String(description='Filter by plan ID', example='PLAN123'),
        'scenarioType': fields.String(description='Scenario type filter', example='base'),
        'includeProjections': fields.Boolean(
            description='Include cashflow and networth projections',
            default=True,
            example=True
        )
    })

    # CashFlow-specific filters
    cashflow_filters_model = api.model('CashFlowFilters', {
        'cashFlowId': fields.String(description='Specific cashflow ID to extract', example='CF001'),
        'scenarioId': fields.String(description='Filter by scenario ID', example='SCENARIO001'),
        'planId': fields.String(description='Filter by plan ID', example='PLAN123'),
        'yearStart': fields.Integer(description='Start year for projections', example=2025, min=1900, max=2100),
        'yearEnd': fields.Integer(description='End year for projections', example=2050, min=1900, max=2100)
    })

    # NetWorth-specific filters
    networth_filters_model = api.model('NetWorthFilters', {
        'netWorthId': fields.String(description='Specific networth ID to extract', example='NW001'),
        'scenarioId': fields.String(description='Filter by scenario ID', example='SCENARIO001'),
        'planId': fields.String(description='Filter by plan ID', example='PLAN123'),
        'yearStart': fields.Integer(description='Start year for projections', example=2025, min=1900, max=2100),
        'yearEnd': fields.Integer(description='End year for projections', example=2050, min=1900, max=2100)
    })

    # Scan configuration model
    scan_config_model = api.model('ScanConfig', {
        'scanId': fields.String(
            required=True, 
            description='Unique identifier for the scan',
            example='emoney-plan-2025-001'
        ),
        'organizationId': fields.String(
            required=True, 
            description='Organization identifier',
            example='org-12345'
        ),
        'type': fields.List(
            fields.String, 
            required=True,
            description='Type of financial plan entity (plan, goal, scenario, cashflow, or networth)',
            example=['plan']
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
        'lastCheckpointAt': fields.String(description='When last checkpoint was created'),
        'entity': fields.String(description='Entity type being processed'),
        'recordsProcessed': fields.Integer(description='Number of records processed')
    })

    # Scan status model
    scan_status_model = api.model('ScanStatus', {
        'scanId': fields.String(description='Scan identifier'),
        'organizationId': fields.String(description='Organization identifier'),
        'type': fields.String(description='Financial plan entity type'),
        'status': fields.String(
            description='Scan status', 
            enum=['pending', 'running', 'completed', 'failed', 'cancelled', 'crashed', 'resuming', 'paused']
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
        'description': fields.String(description='Property description'),
        'required': fields.Boolean(description='Whether property is required')
    })

    # Entity properties model
    entity_properties_model = api.model('EntityProperties', {
        'entityType': fields.String(description='Entity type (plan, goal, scenario, cashflow, networth)'),
        'standard': fields.List(fields.Nested(entity_property_model)),
        'filters': fields.Raw(description='Available filters for this entity type')
    })

    # Plan summary model
    plan_summary_model = api.model('PlanSummary', {
        'PlanID': fields.String(description='Plan identifier'),
        'ClientID': fields.String(description='Client identifier'),
        'PlanName': fields.String(description='Plan name'),
        'PlanStatus': fields.String(description='Plan status'),
        'CreatedDate': fields.String(description='Creation date'),
        'LastModified': fields.String(description='Last modification date')
    })

    # Goal summary model
    goal_summary_model = api.model('GoalSummary', {
        'GoalID': fields.String(description='Goal identifier'),
        'PlanID': fields.String(description='Associated plan ID'),
        'GoalName': fields.String(description='Goal name'),
        'GoalType': fields.String(description='Goal type'),
        'TargetAmount': fields.Float(description='Target amount'),
        'GoalStatus': fields.String(description='Goal status')
    })

    # Scenario summary model
    scenario_summary_model = api.model('ScenarioSummary', {
        'ScenarioID': fields.String(description='Scenario identifier'),
        'PlanID': fields.String(description='Associated plan ID'),
        'ScenarioName': fields.String(description='Scenario name'),
        'ScenarioType': fields.String(description='Scenario type (base, alternative, etc.)'),
        'Description': fields.String(description='Scenario description')
    })

    # Table info model
    table_info_model = api.model('TableInfo', {
        'name': fields.String(description='Table name (plan, goal, scenario, cashflow, networth)'),
        'rowCount': fields.Integer(description='Current row count in database'),
        'extractedCount': fields.Integer(description='Number of records extracted during scan'),
        'primaryKey': fields.String(description='Primary key field name'),
        'description': fields.String(description='Table description')
    })

    # Tables response model
    tables_response_model = api.model('TablesResponse', {
        'scanId': fields.String(description='Scan identifier'),
        'datasetName': fields.String(description='Database dataset name'),
        'tables': fields.List(fields.Nested(table_info_model)),
        'totalTables': fields.Integer(description='Total number of tables'),
        'entityTypes': fields.List(fields.String, description='Available entity types')
    })

    # Results response model
    results_response_model = api.model('ResultsResponse', {
        'scanId': fields.String(description='Scan identifier'),
        'tableName': fields.String(description='Table name (entity type)'),
        'records': fields.List(fields.Raw, description='Array of data records'),
        'pagination': fields.Nested(pagination_model),
        'availableTables': fields.List(fields.String, description='Available table names'),
        'columns': fields.List(fields.String, description='Column names in the table'),
        'entityType': fields.String(description='Entity type of the records')
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
        'daysOld': fields.Integer(description='Days old threshold used'),
        'scansRemoved': fields.List(fields.String, description='List of scan IDs removed')
    })

    # Stream info model
    stream_info_model = api.model('StreamInfo', {
        'topic': fields.String(description='Kafka topic name'),
        'partition': fields.Integer(description='Kafka partition'),
        'offset': fields.Integer(description='Current offset'),
        'totalRecords': fields.Integer(description='Total records streamed'),
        'entityType': fields.String(description='Entity type being streamed')
    })

    # Statistics model
    statistics_model = api.model('Statistics', {
        'totalScans': fields.Integer(description='Total number of scans'),
        'activeScans': fields.Integer(description='Number of active scans'),
        'completedScans': fields.Integer(description='Number of completed scans'),
        'failedScans': fields.Integer(description='Number of failed scans'),
        'totalRecordsExtracted': fields.Integer(description='Total records extracted across all scans'),
        'byEntityType': fields.Raw(description='Statistics broken down by entity type')
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
        'plan_filters_model': plan_filters_model,
        'goal_filters_model': goal_filters_model,
        'scenario_filters_model': scenario_filters_model,
        'cashflow_filters_model': cashflow_filters_model,
        'networth_filters_model': networth_filters_model,
        'scan_config_model': scan_config_model,
        'scan_request_model': scan_request_model,
        'scan_status_model': scan_status_model,
        'checkpoint_info_model': checkpoint_info_model,
        'pagination_model': pagination_model,
        'scan_list_model': scan_list_model,
        'entity_property_model': entity_property_model,
        'entity_properties_model': entity_properties_model,
        'plan_summary_model': plan_summary_model,
        'goal_summary_model': goal_summary_model,
        'scenario_summary_model': scenario_summary_model,
        'table_info_model': table_info_model,
        'tables_response_model': tables_response_model,
        'results_response_model': results_response_model,
        'cleanup_request_model': cleanup_request_model,
        'cleanup_response_model': cleanup_response_model,
        'stream_info_model': stream_info_model,
        'statistics_model': statistics_model,
        'api_response_model': api_response_model
    }