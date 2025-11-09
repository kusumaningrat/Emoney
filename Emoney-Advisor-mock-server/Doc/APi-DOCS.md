# 🏗️ eMoney Advisor Services Suite - Complete Documentation with Example JSON Responses

The eMoney Advisor Services Suite consists of specialized microservices for extracting data from eMoney Advisor platform. Each service is designed to handle specific functional areas with multiple related objects per domain.

---

## 🏗️ Service Architecture

### Core Service (Django-based Orchestration)
- **Framework**: Django with REST API endpoints
- **Purpose**: Orchestrate and manage individual eMoney Advisor extraction services, acting as API Gateway for complex deployments
- **Structure**: Django project with common, external, and internal modules

### Individual Services (Flask-based Extraction)
- **Framework**: Flask with API endpoints
- **Purpose**: Handle specific data object extraction from eMoney Advisor APIs
- **Structure**: Microservices with api, services, models structure
- **Generated with**: `python emoney_gen.py -c <service-config.json>`

### Mock Server (REST API)
- **Framework**: Pure REST API implementation
- **Purpose**: Simulates eMoney Advisor API responses for testing and development
- **Structure**: Lightweight server for mocking eMoney Advisor platform responses

---

## 🌐 API Endpoint JSON Examples

### GET `/api/v1/scan/{scan_id}/status`
```json
{
  "scanId": "scan-12345",
  "status": "running",
  "progress": {
    "total": 500,
    "processed": 200,
    "percentage": 40,
    "current_batch": 2,
    "total_batches": 5
  },
  "error": null
}
```

### GET `/api/v1/scan/list`
```json
{
  "scans": [
    {"scanId": "scan-12345", "status": "completed", "object_type": "Client", "created_at": "2025-11-09T10:00:00Z"},
    {"scanId": "scan-12346", "status": "running", "object_type": "FinancialPlan", "created_at": "2025-11-09T11:00:00Z"}
  ],
  "pagination": {"page": 1, "page_size": 10, "total_pages": 5, "total_items": 50}
}
```

### GET `/api/v1/results/{scan_id}/tables`
```json
{
  "scanId": "scan-12345",
  "tables": ["Client", "Contact", "Household", "Relationship"]
}
```

### GET `/api/v1/results/{scan_id}/result`
```json
{
  "scanId": "scan-12345",
  "table": "Client",
  "data": [
    {"ID": "C001", "Name": "John Doe", "Status": "Active", "Email": "john.doe@example.com"},
    {"ID": "C002", "Name": "Jane Smith", "Status": "Active", "Email": "jane.smith@example.com"}
  ],
  "metadata": {
    "service": "emoney-client-service",
    "extraction_start": "2025-11-09T10:05:00Z",
    "last_updated": "2025-11-09T10:10:00Z"
  }
}
```

### GET `/health`
```json
{
  "service": "emoney-client-service",
  "status": "healthy",
  "timestamp": "2025-11-09T12:00:00Z",
  "framework": "Flask",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "emoney_api_connectivity": "healthy"
  }
}
```

### GET `/stats`
```json
{
  "service": "emoney-client-service",
  "total_scans": 100,
  "completed_scans": 80,
  "failed_scans": 5,
  "running_scans": 15,
  "average_processing_time_seconds": 45
}
```

### GET `/api/v1/pipeline/info`
```json
{
  "service": "emoney-client-service",
  "pipeline_version": "1.0.0",
  "batch_size": 100,
  "last_run": "2025-11-09T11:55:00Z",
  "next_run": "2025-11-09T13:00:00Z"
}
```

---

All remaining services (`FinancialPlanning`, `Account`, `Asset`, `Spending`, `Estate`, `Retirement`, `Insurance`, `Tax`, `Document`, `User`) follow the same endpoints with the corresponding `object_type` in the JSON responses and identical response structures.

---

# Downloadable Markdown Link
You can download the full documentation with JSON examples here:

[Download eMoney Services Full Documentation.md](sandbox:/mnt/data/emoney_services_docs_full.md)

