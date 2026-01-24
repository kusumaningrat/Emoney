# eMoney Account Service - API Documentation

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [Common Response Formats](#common-response-formats)
5. [API Endpoints](#api-endpoints)
6. [Health & Stats Endpoints](#health--stats-endpoints)
7. [Error Handling](#error-handling)
8. [Examples](#examples)
9. [Rate Limiting](#rate-limiting)
10. [Changelog](#changelog)

## 🔍 Overview

The eMoney Service handles extraction of data from the eMoney Advisor platform, including User, Role, Permission, Office, Logon, SharingRule, Plan, Goal, Scenario, CashFlow, NetWorth, Client, Contact, Household, Spouse, Relationship, Account, AccountType, Asset, AssetClass, Liability.

### API Version

- **Version**: 1.0.0
- **Base Path**: `/api`
- **Content Type**: `application/json`
- **Documentation**: Available at `/docs` (Swagger UI)

### Key Features

- **eMoney Advisor API Integration**: Extracts eMoney Service data via eMoney Advisor REST API
- **DLT Integration**: Efficient data loading with PostgreSQL destination
- **Async Processing**: Non-blocking scan operations with real-time status tracking
- **Pause/Resume Support**: Ability to pause and resume scans with checkpoint recovery
- **Multi-Environment**: Separate configurations for dev/staging/prod
- **Comprehensive Monitoring**: Health checks, logging, and pipeline information.

## 🔐 Authentication

The service uses API key authentication for eMoney Advisor platform access.

### Required Credentials

- **API Key**: eMoney Advisor API access token
- **API Secret**: eMoney Advisor API secret (if required)
- **Organization ID**: Organization identifier for multi-tenant support

### Required Permissions

- `account:read` - Read account data
- `account:list` - List accounts
- `investment:read` - Read investment data

### Authentication Headers

```
Authorization: Bearer <token>
Content-Type: application/json
```

## 🌐 Base URLs

### Development

```
http://localhost:4709
```

### Staging

```
http://localhost:5709
```

### Production

```
http://localhost:3709
```

### Swagger Documentation

```
http://localhost:4709/docs
```

## 📊 Common Response Formats

### Success Response

```json
{
  "status": "success",
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

### Error Response (Validation)

```json
{
  "status": "error",
  "message": "Input validation failed",
  "errors": {
    "scanId": "Field is required"
  },
  "timestamp": "2026-01-15T10:30:00Z"
}
```

### Error Response (Application Logic)

```json
{
  "status": "error",
  "error_code": "SCAN_NOT_FOUND",
  "message": "The requested scan was not found",
  "details": {},
  "timestamp": "2026-01-15T10:30:00Z"
}
```

### Pagination Response

```json
{
  "pagination": {
    "current_page": 1,
    "page_size": 50,
    "total_items": 150,
    "total_pages": 3,
    "has_next": true,
    "has_previous": false
  }
}
```

## 🔍 Scan Endpoints

### 1. Start Extraction

**POST** `/api/scan/start`

Initiates a new account data extraction process from eMoney Advisor.

#### Request Body

```json
{
  "config": {
    "scanId": "account-scan-001",
    "organizationId": "org-12345",
    "type": ["account"],
    "auth": {
      "api_key": "your-emoney-api-key",
      "api_secret": "your-emoney-api-secret"
    },
    "filters": {
      "accountTypes": ["Investment", "Liability"],
      "includeInactive": false,
      "dateRange": {
        "startDate": "2026-01-01",
        "endDate": "2026-12-31"
      }
    }
  }
}
```

#### Parameters

| Parameter                | Type   | Required | Description                                                                             |
| ------------------------ | ------ | -------- | --------------------------------------------------------------------------------------- |
| `config.scanId`          | string | Yes      | Unique identifier for the scan (alphanumeric, hyphens, underscores only, max 255 chars) |
| `config.organizationId`  | string | Yes      | Organization identifier                                                                 |
| `config.type`            | array  | Yes      | Service types to scan (must include "account")                                          |
| `config.auth.api_key`    | string | Yes      | eMoney Advisor API key                                                                  |
| `config.auth.api_secret` | string | No       | eMoney Advisor API secret                                                               |

#### Response

```json
{
  "message": "Emoney extraction service started",
  "scanId": "account-scan-001",
  "status": "started"
}
```

#### Status Codes

- **202**: Extraction started successfully
- **400**: Invalid request data
- **409**: Extraction already in progress
- **500**: Internal server error

---

### 2. Get Extraction Status

**GET** `/api/scan/{scan_id}/status`

Retrieves the current status of an extraction process.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response (Existing Extraction)

```json
{
  "scanId": "account-scan-001",
  "organizationId": "org-12345",
  "type": "account",
  "status": "running",
  "startTime": "2026-01-15T10:30:00Z",
  "endTime": null,
  "lastHeartbeat": "2026-01-15T10:35:00Z",
  "recordsExtracted": 245,
  "errorMessage": null,
  "config": {
    "auth": {...},
    "filters": {...}
  },
  "metadata": {
    "batch_count": 3,
    "current_phase": "accounts"
  }
}
```

#### Response (Non-existent Extraction)

```json
{
  "scanId": null,
  "status": "not_found",
  "message": "Scan not found"
}
```

#### Status Values

- **pending**: Extraction queued but not started
- **running**: Extraction in progress
- **paused**: Extraction paused by user
- **resuming**: Extraction resuming from checkpoint
- **completed**: Extraction finished successfully
- **failed**: Extraction failed with error
- **cancelled**: Extraction cancelled by user
- **crashed**: Extraction crashed unexpectedly
- **max_batches_reached**: Maximum batches limit reached

#### Status Codes

- **200**: Always returns 200 (check `status` field for actual state)
- **400**: Invalid scan ID format

---

### 3. Pause Extraction

**POST** `/api/scan/{scan_id}/pause`

Pauses an ongoing extraction process.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response

```json
{
  "message": "Scan paused successfully",
  "scanId": "account-scan-001",
  "status": "paused"
}
```

#### Status Codes

- **200**: Extraction paused successfully
- **400**: Invalid scan ID format or extraction cannot be paused
- **404**: Extraction not found
- **500**: Internal server error

---

### 4. Resume Extraction

**POST** `/api/scan/{scan_id}/resume`

Resumes a paused extraction process.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response

```json
{
  "message": "Scan resumed successfully",
  "scanId": "account-scan-001",
  "status": "resuming"
}
```

#### Status Codes

- **200**: Extraction resumed successfully
- **400**: Invalid scan ID format or extraction cannot be resumed
- **404**: Extraction not found
- **500**: Internal server error

---

### 5. Cancel Extraction

**POST** `/api/scan/{scan_id}/cancel`

Cancels an ongoing extraction process.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response

```json
{
  "message": "Extraction cancelled successfully",
  "scanId": "account-scan-001",
  "status": "cancelled"
}
```

#### Status Codes

- **200**: Extraction cancelled successfully
- **400**: Invalid scan ID format or extraction cannot be cancelled
- **404**: Extraction not found
- **500**: Internal server error

---

### 6. Remove Extraction

**DELETE** `/api/scan/{scan_id}/remove`

Removes an extraction and all associated data from the system.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response

```json
{
  "message": "Scan and 1,234 records removed successfully",
  "scanId": "account-scan-001",
  "status": "removed",
  "recordsDeleted": 1234
}
```

#### Status Codes

- **200**: Extraction removed successfully
- **400**: Invalid scan ID format or extraction cannot be removed
- **404**: Extraction not found
- **500**: Internal server error

---

### 7. List Scans

**GET** `/api/scan/list`

Retrieves a list of all scans with optional filtering and pagination.

#### Query Parameters

| Parameter        | Type    | Required | Default | Description                         |
| ---------------- | ------- | -------- | ------- | ----------------------------------- |
| `organizationId` | string  | No       | -       | Filter by organization ID           |
| `status`         | string  | No       | -       | Filter by status                    |
| `type`           | string  | No       | -       | Filter by scan type                 |
| `limit`          | integer | No       | 20      | Number of scans per page (max: 100) |
| `offset`         | integer | No       | 0       | Number of scans to skip             |

#### Response

```json
{
  "scans": [
    {
      "scanId": "account-scan-001",
      "organizationId": "org-12345",
      "type": "account",
      "status": "completed",
      "startTime": "2024-01-15T10:30:00Z",
      "endTime": "2024-01-15T10:45:00Z",
      "recordsExtracted": 1500
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 45
  }
}
```

#### Status Codes

- **200**: Scans retrieved successfully
- **400**: Invalid query parameters
- **500**: Internal server error

---

### 8. Get Scan Statistics

**GET** `/api/scan/statistics`

Retrieves statistics about scans.

#### Query Parameters

| Parameter        | Type   | Required | Default | Description               |
| ---------------- | ------ | -------- | ------- | ------------------------- |
| `organizationId` | string | No       | -       | Filter by organization ID |

#### Response

```json
{
  "total_scans": 45,
  "active_scans": 3,
  "completed_scans": 40,
  "failed_scans": 2,
  "total_records_extracted": 150000,
  "average_records_per_scan": 3333,
  "scans_by_status": {
    "pending": 0,
    "running": 3,
    "completed": 40,
    "failed": 2,
    "cancelled": 0
  }
}
```

#### Status Codes

- **200**: Statistics retrieved successfully
- **500**: Internal server error

---

## 📦 Results Endpoints

### 9. Get Available Tables

**GET** `/api/results/{scan_id}/tables`

Retrieves the list of available tables for a completed scan.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Response

```json
{
  "scanId": "account-scan-001",
  "tables": [
    {
      "name": "accounts",
      "record_count": 500,
      "schema": "emoney_account_dev"
    },
    {
      "name": "investments",
      "record_count": 300,
      "schema": "emoney_account_dev"
    },
    {
      "name": "liabilities",
      "record_count": 200,
      "schema": "emoney_account_dev"
    }
  ]
}
```

#### Status Codes

- **200**: Tables retrieved successfully
- **404**: Scan not found
- **500**: Internal server error

---

### 10. Get Scan Results

**GET** `/api/results/{scan_id}/result`

Retrieves paginated extraction results with optional table selection.

#### Path Parameters

| Parameter | Type   | Required | Description            |
| --------- | ------ | -------- | ---------------------- |
| `scan_id` | string | Yes      | Unique scan identifier |

#### Query Parameters

| Parameter   | Type    | Required | Default | Description                 |
| ----------- | ------- | -------- | ------- | --------------------------- |
| `tableName` | string  | No       | -       | Specific table to query     |
| `limit`     | integer | No       | 100     | Records per page (max: 500) |
| `offset`    | integer | No       | 0       | Number of records to skip   |

#### Response

```json
{
  "scanId": "account-scan-001",
  "tableName": "accounts",
  "data": [
    {
      "account_id": "ACC-001",
      "account_name": "Investment Account",
      "account_type": "Investment",
      "balance": 50000.0,
      "owner": "John Doe"
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0,
    "total": 500
  }
}
```

#### Status Codes

- **200**: Results retrieved successfully
- **400**: Invalid query parameters
- **404**: Scan not found
- **500**: Internal server error

---

## 🏥 Health & Stats Endpoints

### 11. Health Check

**GET** `/api/health`

Returns the overall health status of the service.

#### Response (Healthy)

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "eMoney Account Service",
  "version": "1.0.0",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "emoney_api": "healthy"
  }
}
```

#### Response (Unhealthy)

```json
{
  "status": "unhealthy",
  "timestamp": "2026-01-15T10:30:00Z",
  "service": "eMoney Service",
  "version": "1.0.0",
  "checks": {
    "database": "unhealthy: connection timeout",
    "cache": "healthy",
    "emoney_api": "degraded: high latency"
  }
}
```

#### Status Codes

- **200**: Service is healthy
- **503**: Service is unhealthy

---

### 12. Service Statistics

**GET** `/api/stats`

Returns comprehensive service statistics and performance metrics.

#### Response

```json
{
  "service": "eMoney Service",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "total_scans": 150,
  "active_scans": 5,
  "total_records_extracted": 250000,
  "database": {
    "pool_size": 10,
    "checked_in": 8,
    "checked_out": 2,
    "overflow": 0
  }
}
```

#### Status Codes

- **200**: Statistics retrieved successfully
- **500**: Internal server error

---

### 13. Pipeline Info

**GET** `/api/pipeline/info`

Returns information about the DLT pipeline configuration.

#### Response

```json
{
  "pipeline_name": "emoney_service_pipeline_dev",
  "destination": "postgresql",
  "schema": "emoney_service_dev",
  "database": {
    "host": "postgres_dev",
    "port": 5432,
    "database": "emoney_service_data_dev"
  },
  "configuration": {
    "batch_size": 100,
    "max_concurrent_scans": 3
  }
}
```

#### Status Codes

- **200**: Pipeline info retrieved successfully
- **500**: Internal server error

---

## 🛠️ Maintenance Endpoints

### 14. Cleanup Old Scans

**POST** `/api/maintenance/cleanup`

Cleans up old scan results based on retention policy.

#### Request Body

```json
{
  "daysOld": 30,
  "statuses": ["completed", "failed", "cancelled"]
}
```

#### Response

```json
{
  "message": "Cleanup completed",
  "scans_removed": 15,
  "records_deleted": 25000
}
```

#### Status Codes

- **200**: Cleanup completed successfully
- **400**: Invalid request data
- **500**: Internal server error

---

### 15. Detect Crashed Jobs

**POST** `/api/maintenance/detect-crashed`

Detects and marks crashed jobs based on heartbeat timeout.

#### Query Parameters

| Parameter        | Type    | Required | Default | Description                  |
| ---------------- | ------- | -------- | ------- | ---------------------------- |
| `timeoutMinutes` | integer | No       | 10      | Heartbeat timeout in minutes |

#### Response

```json
{
  "message": "Crash detection completed",
  "crashed_jobs_detected": 2,
  "jobs_marked": ["account-scan-005", "account-scan-012"]
}
```

#### Status Codes

- **200**: Detection completed successfully
- **400**: Invalid timeout value
- **500**: Internal server error

---

## ⚠️ Error Handling

### Error Response Formats

#### Validation Errors (400)

```json
{
  "status": "error",
  "error_code": "VALIDATION_ERROR",
  "message": "Input validation failed",
  "errors": {
    "scanId": "Scan ID is required",
    "organizationId": "Invalid organization ID format"
  },
  "timestamp": "2026-01-15T10:30:00Z"
}
```

#### Not Found Errors (404)

```json
{
  "status": "error",
  "error_code": "NOT_FOUND",
  "message": "Scan not found",
  "scanId": "account-scan-999",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Conflict Errors (409)

```json
{
  "status": "error",
  "error_code": "CONFLICT",
  "message": "Scan already in progress",
  "scanId": "account-scan-001",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

#### Server Errors (500)

```json
{
  "status": "error",
  "error_code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Code                        | Description                                |
| --------------------------- | ------------------------------------------ |
| `VALIDATION_ERROR`          | Input validation failed                    |
| `NOT_FOUND`                 | Resource not found                         |
| `CONFLICT`                  | Resource already exists or state conflict  |
| `INTERNAL_ERROR`            | Server error                               |
| `SCAN_IN_PROGRESS`          | Scan already running                       |
| `INVALID_STATUS_TRANSITION` | Cannot perform operation in current status |

---

## 📚 Examples

### Complete Extraction Workflow

#### 1. Start Extraction

```bash
curl -X POST "http://localhost:4709/api/scan/start" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "scanId": "account-extract-001",
      "organizationId": "org-12345",
      "type": ["account"],
      "auth": {
        "api_key": "your-emoney-api-key"
      },
      "filters": {
        "accountTypes": ["Investment"],
        "includeInactive": false
      }
    }
  }'
```

#### 2. Monitor Progress

```bash
curl "http://localhost:4709/api/scan/account-extract-001/status"
```

#### 3. Pause if Needed

```bash
curl -X POST "http://localhost:4709/api/scan/account-extract-001/pause"
```

#### 4. Resume Scan

```bash
curl -X POST "http://localhost:4709/api/scan/account-extract-001/resume"
```

#### 5. Get Available Tables

```bash
curl "http://localhost:4709/api/results/account-extract-001/tables"
```

#### 6. Get Results

```bash
curl "http://localhost:4709/api/results/account-extract-001/result?tableName=accounts&limit=50"
```

#### 7. Cancel Extraction (if needed)

```bash
curl -X POST "http://localhost:4709/api/scan/account-extract-001/cancel"
```

#### 8. Remove Extraction (cleanup)

```bash
curl -X DELETE "http://localhost:4709/api/scan/account-extract-001/remove"
```

### Python Examples

#### Start Extraction

```python
import requests

url = "http://localhost:4709/api/scan/start"
payload = {
    "config": {
        "scanId": "python-account-001",
        "organizationId": "org-12345",
        "type": ["account"],
        "auth": {
            "api_key": "your-emoney-api-key"
        },
        "filters": {
            "accountTypes": ["Investment", "Liability"]
        }
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

#### Monitor Progress

```python
import requests
import time

scan_id = "python-account-001"
url = f"http://localhost:4709/api/scan/{scan_id}/status"

while True:
    response = requests.get(url)
    status = response.json()

    print(f"Status: {status['status']}, Records: {status.get('recordsExtracted', 0)}")

    if status['status'] in ['completed', 'failed', 'cancelled']:
        break

    time.sleep(10)  # Check every 10 seconds
```

#### Get Paginated Results

```python
import requests

scan_id = "python-account-001"
offset = 0
limit = 100
all_records = []

while True:
    url = f"http://localhost:4709/api/results/{scan_id}/result?tableName=accounts&limit={limit}&offset={offset}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        all_records.extend(data['data'])

        if offset + limit >= data['pagination']['total']:
            break

        offset += limit
    else:
        print(f"Error: {response.status_code}")
        break

print(f"Total records retrieved: {len(all_records)}")
```

---

## ⚡ Rate Limiting

- **Rate Limit**: 100 requests per hour (configurable)
- **Burst Limit**: 10 requests per minute
- **Headers**: Rate limit information returned in response headers

---

## 📝 Changelog

### Version 1.0.0 (2024-01-15)

- Initial release
- Support for account data extraction
- Pause/resume functionality
- DLT integration with PostgreSQL
- Multi-environment configuration
- Comprehensive API endpoints
- Health check and monitoring

---

**API Documentation Version**: 1.0.0  
**Last Updated**: 2024-12-12  
**Service**: eMoney Service
