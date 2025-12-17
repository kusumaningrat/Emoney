"""
Swagger/OpenAPI schema definitions for eMoney Identity Service Extraction API
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

    # Filters model for identity entity extraction
    filters_model = api.model('Filters', {
        'dateRange': fields.Nested(date_range_model, description='Date range filter'),
        'includeInactive': fields.Boolean(
            description='Include inactive/disabled entities',
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

    # User-specific filters
    user_filters_model = api.model('UserFilters', {
        'userId': fields.String(description='Specific user ID to extract', example='USER123'),
        'email': fields.String(description='Filter by email address', example='user@example.com'),
        'username': fields.String(description='Filter by username', example='jdoe'),
        'officeId': fields.String(description='Filter by office ID', example='OFFICE456'),
        'roleId': fields.String(description='Filter by role ID', example='ROLE789'),
        'userStatus': fields.String(
            description='User status filter',
            enum=['active', 'inactive', 'suspended', 'all'],
            default='active',
            example='active'
        ),
        'includeDeleted': fields.Boolean(
            description='Include deleted users',
            default=False,
            example=False
        )
    })

    # Role-specific filters
    role_filters_model = api.model('RoleFilters', {
        'roleId': fields.String(description='Specific role ID to extract', example='ROLE789'),
        'roleName': fields.String(description='Filter by role name', example='Administrator'),
        'roleType': fields.String(
            description='Role type filter',
            enum=['system', 'custom', 'all'],
            default='all',
            example='system'
        ),
        'isActive': fields.Boolean(description='Filter by active status', example=True)
    })

    # Permission-specific filters
    permission_filters_model = api.model('PermissionFilters', {
        'permissionId': fields.String(description='Specific permission ID to extract', example='PERM001'),
        'roleId': fields.String(description='Filter by role ID', example='ROLE789'),
        'userId': fields.String(description='Filter by user ID', example='USER123'),
        'permissionType': fields.String(description='Permission type filter', example='data_access'),
        'resource': fields.String(description='Resource filter', example='client_data'),
        'action': fields.String(
            description='Action filter',
            enum=['read', 'write', 'delete', 'execute', 'admin', 'all'],
            default='all',
            example='read'
        )
    })

    # Office-specific filters
    office_filters_model = api.model('OfficeFilters', {
        'officeId': fields.String(description='Specific office ID to extract', example='OFFICE456'),
        'officeName': fields.String(description='Filter by office name', example='New York Office'),
        'parentOfficeId': fields.String(description='Filter by parent office ID', example='OFFICE001'),
        'officeStatus': fields.String(
            description='Office status filter',
            enum=['active', 'inactive', 'all'],
            default='active',
            example='active'
        ),
        'includeSubOffices': fields.Boolean(
            description='Include sub-offices in hierarchy',
            default=False,
            example=False
        )
    })

    # Logon-specific filters
    logon_filters_model = api.model('LogonFilters', {
        'logonId': fields.String(description='Specific logon ID to extract', example='LOGON001'),
        'userId': fields.String(description='Filter by user ID', example='USER123'),
        'loginDateStart': fields.String(
            description='Start date for login history (YYYY-MM-DD)',
            example='2025-01-01'
        ),
        'loginDateEnd': fields.String(
            description='End date for login history (YYYY-MM-DD)',
            example='2025-12-31'
        ),
        'logonStatus': fields.String(
            description='Logon status filter',
            enum=['success', 'failed', 'locked', 'all'],
            default='all',
            example='success'
        ),
        'ipAddress': fields.String(description='Filter by IP address', example='192.168.1.100')
    })

    # SharingRule-specific filters
    sharingrule_filters_model = api.model('SharingRuleFilters', {
        'sharingRuleId': fields.String(description='Specific sharing rule ID to extract', example='SHARE001'),
        'userId': fields.String(description='Filter by user ID (owner)', example='USER123'),
        'sharedWithUserId': fields.String(description='Filter by shared with user ID', example='USER456'),
        'officeId': fields.String(description='Filter by office ID', example='OFFICE456'),
        'resourceType': fields.String(description='Resource type filter', example='client'),
        'resourceId': fields.String(description='Resource ID filter', example='CLIENT789'),
        'accessLevel': fields.String(
            description='Access level filter',
            enum=['view', 'edit', 'full', 'all'],
            default='all',
            example='view'
        ),
        'isActive': fields.Boolean(description='Filter by active status', example=True)
    })

    # Scan configuration model
    scan_config_model = api.model('ScanConfig', {
        'scanId': fields.String(
            required=True, 
            description='Unique identifier for the scan',
            example='emoney-identity-2025-001'
        ),
        'organizationId': fields.String(
            required=True, 
            description='Organization identifier',
            example='org-12345'
        ),
        'type': fields.List(
            fields.String, 
            required=True,
            description='Type of identity entity (user, role, permission, office, logon, or sharingrule)',
            example=['user']
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
        'type': fields.String(description='Identity entity type'),
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
        'entityType': fields.String(description='Entity type (user, role, permission, office, logon, sharingrule)'),
        'standard': fields.List(fields.Nested(entity_property_model)),
        'filters': fields.Raw(description='Available filters for this entity type')
    })

    # User summary model
    user_summary_model = api.model('UserSummary', {
        'UserID': fields.String(description='User identifier'),
        'Username': fields.String(description='Username'),
        'Email': fields.String(description='Email address'),
        'FirstName': fields.String(description='First name'),
        'LastName': fields.String(description='Last name'),
        'OfficeID': fields.String(description='Office identifier'),
        'RoleID': fields.String(description='Role identifier'),
        'UserStatus': fields.String(description='User status'),
        'CreatedDate': fields.String(description='Creation date'),
        'LastLogin': fields.String(description='Last login date')
    })

    # Role summary model
    role_summary_model = api.model('RoleSummary', {
        'RoleID': fields.String(description='Role identifier'),
        'RoleName': fields.String(description='Role name'),
        'RoleType': fields.String(description='Role type (system/custom)'),
        'Description': fields.String(description='Role description'),
        'IsActive': fields.Boolean(description='Active status'),
        'PermissionCount': fields.Integer(description='Number of permissions')
    })

    # Permission summary model
    permission_summary_model = api.model('PermissionSummary', {
        'PermissionID': fields.String(description='Permission identifier'),
        'RoleID': fields.String(description='Associated role ID'),
        'PermissionType': fields.String(description='Permission type'),
        'Resource': fields.String(description='Resource name'),
        'Action': fields.String(description='Allowed action'),
        'Description': fields.String(description='Permission description')
    })

    # Office summary model
    office_summary_model = api.model('OfficeSummary', {
        'OfficeID': fields.String(description='Office identifier'),
        'OfficeName': fields.String(description='Office name'),
        'ParentOfficeID': fields.String(description='Parent office ID'),
        'OfficeStatus': fields.String(description='Office status'),
        'Address': fields.String(description='Office address'),
        'UserCount': fields.Integer(description='Number of users')
    })

    # Logon summary model
    logon_summary_model = api.model('LogonSummary', {
        'LogonID': fields.String(description='Logon identifier'),
        'UserID': fields.String(description='User identifier'),
        'LoginDateTime': fields.String(description='Login date and time'),
        'LogonStatus': fields.String(description='Logon status (success/failed)'),
        'IPAddress': fields.String(description='IP address'),
        'UserAgent': fields.String(description='User agent string'),
        'SessionDuration': fields.Integer(description='Session duration in minutes')
    })

    # SharingRule summary model
    sharingrule_summary_model = api.model('SharingRuleSummary', {
        'SharingRuleID': fields.String(description='Sharing rule identifier'),
        'UserID': fields.String(description='Owner user ID'),
        'SharedWithUserID': fields.String(description='Shared with user ID'),
        'ResourceType': fields.String(description='Resource type'),
        'ResourceID': fields.String(description='Resource identifier'),
        'AccessLevel': fields.String(description='Access level (view/edit/full)'),
        'IsActive': fields.Boolean(description='Active status'),
        'CreatedDate': fields.String(description='Creation date')
    })

    # Table info model
    table_info_model = api.model('TableInfo', {
        'name': fields.String(description='Table name (user, role, permission, office, logon, sharingrule)'),
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
        'user_filters_model': user_filters_model,
        'role_filters_model': role_filters_model,
        'permission_filters_model': permission_filters_model,
        'office_filters_model': office_filters_model,
        'logon_filters_model': logon_filters_model,
        'sharingrule_filters_model': sharingrule_filters_model,
        'scan_config_model': scan_config_model,
        'scan_request_model': scan_request_model,
        'scan_status_model': scan_status_model,
        'checkpoint_info_model': checkpoint_info_model,
        'pagination_model': pagination_model,
        'scan_list_model': scan_list_model,
        'entity_property_model': entity_property_model,
        'entity_properties_model': entity_properties_model,
        'user_summary_model': user_summary_model,
        'role_summary_model': role_summary_model,
        'permission_summary_model': permission_summary_model,
        'office_summary_model': office_summary_model,
        'logon_summary_model': logon_summary_model,
        'sharingrule_summary_model': sharingrule_summary_model,
        'table_info_model': table_info_model,
        'tables_response_model': tables_response_model,
        'results_response_model': results_response_model,
        'cleanup_request_model': cleanup_request_model,
        'cleanup_response_model': cleanup_response_model,
        'stream_info_model': stream_info_model,
        'statistics_model': statistics_model,
        'api_response_model': api_response_model
    }