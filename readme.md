# 🏗️ eMoney Advisor Services Suite - Complete Documentation

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

## 🌐 Complete eMoney Advisor Services Overview (Sorted by Port)

| **Service**                      | **Group**                      | **Dev Port** | **Stage Port** | **Prod Port** | **Framework** | **Purpose**                             | **Objects**                            |
|----------------------------------|--------------------------------|--------------|----------------|---------------|---------------|-----------------------------------------|----------------------------------------|
| eMoney Core Service              | Core Infrastructure            | 4730         | 5730           | 3730          | Django        | API Gateway and request routing         | All objects                            |
| eMoney Client Service            | Client & Relationship Mgmt     | 4731         | 5731           | 3731          | Flask         | Extract client data                     | `Client`, `Contact`, `Household`, `Relationship` |
| eMoney Financial Planning Service| Financial Planning             | 4732         | 5732           | 3732          | Flask         | Extract financial planning data         | `FinancialPlan`, `Goal`, `Scenario`, `CashFlow` |
| eMoney Account Service           | Account Management             | 4733         | 5733           | 3733          | Flask         | Extract account data                    | `Account`, `AccountType`, `Investment`, `Liability` |
| eMoney Asset Service             | Asset Management               | 4734         | 5734           | 3734          | Flask         | Extract asset data                      | `Asset`, `AssetClass`, `Allocation`, `Security` |
| eMoney Spending Service          | Spending & Budget Management   | 4735         | 5735           | 3735          | Flask         | Extract spending data                   | `Spending`, `Budget`, `Expense`, `Income` |
| eMoney Estate Service            | Estate Planning                | 4736         | 5736           | 3736          | Flask         | Extract estate planning data            | `Estate`, `Will`, `Trust`, `Beneficiary` |
| eMoney Retirement Service        | Retirement Planning            | 4737         | 5737           | 3737          | Flask         | Extract retirement planning data        | `RetirementPlan`, `Pension`, `SocialSecurity`, `RMD` |
| eMoney Insurance Service         | Insurance Planning             | 4738         | 5738           | 3738          | Flask         | Extract insurance data                  | `Insurance`, `Policy`, `Coverage`, `Premium` |
| eMoney Tax Service               | Tax Planning                   | 4739         | 5739           | 3739          | Flask         | Extract tax planning data               | `TaxPlan`, `TaxBracket`, `Deduction`, `Credit` |
| eMoney Document Service          | Document Management            | 4708         | 5708           | 3708          | Flask         | Extract document data                   | `Document`, `Vault`, `FileType`, `Attachment` |
| eMoney User Service              | User & Access Management       | 4709         | 5709           | 3709          | Flask         | Extract user and access data            | `User`, `Role`, `Permission`, `Advisor`, `Firm` |
| Mock Server                      | Core Infrastructure            | 6100         | 6100           | 6100          | REST API      | Simulates eMoney Advisor API responses  | `Mock Data`                            |

## 📊 Service Summary

**Total Services:** 13 (including Core Service and Mock Server)  

**Framework Distribution:**
- **Django:** 1 service (Core Service - API Gateway)
- **Flask:** 11 services (All microservices)  
- **REST API:** 1 service (Mock Server)

**Service Groups:** 10 logical groups with clear separation of concerns

---

# 🚪 eMoney Core Service (Django)

The eMoney Core Service routes requests to appropriate domain services and handles authentication/authorization logic.

## 📋 Overview

| **Service**     | eMoney Core Service                             |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4730                                            |
| **Stage Port**  | 5730                                            |
| **Prod Port**   | 3730                                            |
| **Framework**   | Django                                          |
| **Purpose**     | API Gateway and request routing                |
| **Objects**     | Routes to all domain services                  |

## 🌐 API Endpoints
1. `POST /api/v1/scan/start` - Start a new data extraction scan
2. `GET /api/v1/scan/{scan_id}/status` - Get the status of a specific scan
3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel a running scan
4. `POST /api/v1/scan/{scan_id}/pause` - Pause a running scan
5. `POST /api/v1/scan/{scan_id}/resume` - Resume a paused scan
6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove a scan and its data
7. `GET /api/v1/scan/list` - List all scans with filtering and pagination
8. `GET /api/v1/scan/statistics` - Get scan statistics
9. `GET /api/v1/results/{scan_id}/tables` - Get available tables for completed scan
10. `GET /api/v1/results/{scan_id}/result` - Retrieve scan results with table selection
11. `GET /api/v1/pipeline/info` - Get pipeline configuration info
12. `POST /api/v1/maintenance/cleanup` - Clean up old scan results
13. `POST /api/v1/maintenance/detect-crashed` - Detect and mark crashed jobs
14. `GET /health` - Health check endpoint
15. `GET /stats` - Get service statistics
16. `GET /docs/` - Swagger API documentation

---

# 👤 eMoney Client Service (Flask)

The eMoney Client Service handles the extraction of client and relationship data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Client Service                           |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4731                                            |
| **Stage Port**  | 5731                                            |
| **Prod Port**   | 3731                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract client data from eMoney Advisor APIs   |
| **Objects**     | `Client`, `Contact`, `Household`, `Relationship` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Client Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Client Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Client Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Client Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Client Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Client Data Scan
### 7. `GET /api/v1/scan/list` - List Client Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Client Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Client Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Client Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Client Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Client Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Client Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 📝 eMoney Financial Planning Service (Flask)

The eMoney Financial Planning Service handles the extraction of financial planning data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Financial Planning Service               |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4732                                            |
| **Stage Port**  | 5732                                            |
| **Prod Port**   | 3732                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract financial planning data from eMoney Advisor APIs |
| **Objects**     | `FinancialPlan`, `Goal`, `Scenario`, `CashFlow` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Financial Planning Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Financial Planning Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Financial Planning Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Financial Planning Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Financial Planning Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Financial Planning Data Scan
### 7. `GET /api/v1/scan/list` - List Financial Planning Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Financial Planning Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Financial Planning Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Financial Planning Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Financial Planning Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Financial Planning Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Financial Planning Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 🏦 eMoney Account Service (Flask)

The eMoney Account Service handles the extraction of account data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Account Service                          |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4733                                            |
| **Stage Port**  | 5733                                            |
| **Prod Port**   | 3733                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract account data from eMoney Advisor APIs  |
| **Objects**     | `Account`, `AccountType`, `Investment`, `Liability` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Account Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Account Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Account Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Account Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Account Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Account Data Scan
### 7. `GET /api/v1/scan/list` - List Account Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Account Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Account Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Account Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Account Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Account Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Account Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 💰 eMoney Asset Service (Flask)

The eMoney Asset Service handles the extraction of asset data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Asset Service                            |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4734                                            |
| **Stage Port**  | 5734                                            |
| **Prod Port**   | 3734                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract asset data from eMoney Advisor APIs    |
| **Objects**     | `Asset`, `AssetClass`, `Allocation`, `Security` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Asset Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Asset Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Asset Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Asset Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Asset Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Asset Data Scan
### 7. `GET /api/v1/scan/list` - List Asset Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Asset Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Asset Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Asset Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Asset Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Asset Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Asset Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 💵 eMoney Spending Service (Flask)

The eMoney Spending Service handles the extraction of spending and budget data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Spending Service                         |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4735                                            |
| **Stage Port**  | 5735                                            |
| **Prod Port**   | 3735                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract spending data from eMoney Advisor APIs |
| **Objects**     | `Spending`, `Budget`, `Expense`, `Income`      |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Spending Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Spending Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Spending Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Spending Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Spending Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Spending Data Scan
### 7. `GET /api/v1/scan/list` - List Spending Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Spending Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Spending Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Spending Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Spending Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Spending Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Spending Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 🏛️ eMoney Estate Service (Flask)

The eMoney Estate Service handles the extraction of estate planning data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Estate Service                           |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4736                                            |
| **Stage Port**  | 5736                                            |
| **Prod Port**   | 3736                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract estate planning data from eMoney Advisor APIs |
| **Objects**     | `Estate`, `Will`, `Trust`, `Beneficiary`       |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Estate Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Estate Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Estate Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Estate Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Estate Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Estate Data Scan
### 7. `GET /api/v1/scan/list` - List Estate Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Estate Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Estate Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Estate Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Estate Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Estate Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Estate Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 🏖️ eMoney Retirement Service (Flask)

The eMoney Retirement Service handles the extraction of retirement planning data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Retirement Service                       |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4737                                            |
| **Stage Port**  | 5737                                            |
| **Prod Port**   | 3737                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract retirement planning data from eMoney Advisor APIs |
| **Objects**     | `RetirementPlan`, `Pension`, `SocialSecurity`, `RMD` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Retirement Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Retirement Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Retirement Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Retirement Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Retirement Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Retirement Data Scan
### 7. `GET /api/v1/scan/list` - List Retirement Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Retirement Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Retirement Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Retirement Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Retirement Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Retirement Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Retirement Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 🛡️ eMoney Insurance Service (Flask)

The eMoney Insurance Service handles the extraction of insurance data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Insurance Service                        |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4738                                            |
| **Stage Port**  | 5738                                            |
| **Prod Port**   | 3738                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract insurance data from eMoney Advisor APIs |
| **Objects**     | `Insurance`, `Policy`, `Coverage`, `Premium`   |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Insurance Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Insurance Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Insurance Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Insurance Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Insurance Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Insurance Data Scan
### 7. `GET /api/v1/scan/list` - List Insurance Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Insurance Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Insurance Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Insurance Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Insurance Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Insurance Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Insurance Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 📊 eMoney Tax Service (Flask)

The eMoney Tax Service handles the extraction of tax planning data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Tax Service                              |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4739                                            |
| **Stage Port**  | 5739                                            |
| **Prod Port**   | 3739                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract tax planning data from eMoney Advisor APIs |
| **Objects**     | `TaxPlan`, `TaxBracket`, `Deduction`, `Credit` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Tax Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Tax Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Tax Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Tax Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Tax Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Tax Data Scan
### 7. `GET /api/v1/scan/list` - List Tax Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Tax Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Tax Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Tax Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Tax Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Tax Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Tax Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 📄 eMoney Document Service (Flask)

The eMoney Document Service handles the extraction of document data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney Document Service                         |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4708                                            |
| **Stage Port**  | 5708                                            |
| **Prod Port**   | 3708                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract document data from eMoney Advisor APIs |
| **Objects**     | `Document`, `Vault`, `FileType`, `Attachment`  |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start Document Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get Document Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel Document Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause Document Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume Document Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove Document Data Scan
### 7. `GET /api/v1/scan/list` - List Document Data Scans
### 8. `GET /api/v1/scan/statistics` - Get Document Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available Document Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve Document Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get Document Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old Document Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed Document Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 👥 eMoney User Service (Flask)

The eMoney User Service handles the extraction of user and access data from eMoney Advisor platform.

## 📋 Overview

| **Service**     | eMoney User Service                             |
|-----------------|-------------------------------------------------|
| **Dev Port**    | 4709                                            |
| **Stage Port**  | 5709                                            |
| **Prod Port**   | 3709                                            |
| **Framework**   | Flask                                           |
| **Purpose**     | Extract user and access data from eMoney Advisor APIs |
| **Objects**     | `User`, `Role`, `Permission`, `Advisor`, `Firm` |
| **Batch Size**  | 100 (default)                                   |

## 🌐 API Endpoints

### 1. `POST /api/v1/scan/start` - Start User Data Scan
### 2. `GET /api/v1/scan/{scan_id}/status` - Get User Data Scan Status
### 3. `POST /api/v1/scan/{scan_id}/cancel` - Cancel User Data Scan
### 4. `POST /api/v1/scan/{scan_id}/pause` - Pause User Data Scan
### 5. `POST /api/v1/scan/{scan_id}/resume` - Resume User Data Scan
### 6. `DELETE /api/v1/scan/{scan_id}/remove` - Remove User Data Scan
### 7. `GET /api/v1/scan/list` - List User Data Scans
### 8. `GET /api/v1/scan/statistics` - Get User Data Scan Statistics
### 9. `GET /api/v1/results/{scan_id}/tables` - Get Available User Data Tables
### 10. `GET /api/v1/results/{scan_id}/result` - Retrieve User Data Scan Results
### 11. `GET /api/v1/pipeline/info` - Get User Data Pipeline Info
### 12. `POST /api/v1/maintenance/cleanup` - Clean up Old User Data Scan Results
### 13. `POST /api/v1/maintenance/detect-crashed` - Detect and Mark Crashed User Data Jobs
### 14. `GET /health` - Health Check
### 15. `GET /stats` - Service Statistics
### 16. `GET /docs/` - Swagger API Documentation

---

# 🧪 Mock Server (REST API)

A simple mock server to simulate responses from eMoney Advisor APIs for testing purposes.

## 📋 Overview

| **Service**     | Mock Server                                     |
|-----------------|-------------------------------------------------|
| **Port**        | 6100 (all environments)                        |
| **Framework**   | REST API                                        |
| **Purpose**     | Simulate eMoney Advisor API responses for testing |
| **Objects**     | `Mock Data`                                     |

## 🌐 API Endpoints

### 1. `GET /mock/clients` - Get Sample Client Data
### 2. `GET /mock/financial-plans` - Get Sample Financial Planning Data
### 3. `GET /mock/accounts` - Get Sample Account Data
### 4. `GET /mock/assets` - Get Sample Asset Data
### 5. `GET /mock/spending` - Get Sample Spending Data
### 6. `POST /mock/echo` - Echo Request Body
### 7. `GET /health` - Health Check (mock)

---

## ⚙️ Common Configuration

### Request Structure
```json
{
  "config": {
    "scanId": "unique-scan-identifier",
    "type": ["client", "financial-planning", "account", "asset", "spending", "estate", "retirement", "insurance", "tax", "document", "user"],
    "auth": {
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    },
    "params": {
      "batchSize": 100,
      "fields": ["ID", "Name", "Type", "Status"],
      "filters": {
        "status": "Active",
        "created_date": "2024-01-01"
      },
      "firm_id": "firm-identifier"
    }
  }
}
```

### Response Structure
```json
{
  "scanId": "unique-scan-identifier",
  "status": "started|running|completed|failed|cancelled|paused",
  "progress": {
    "total": 1000,
    "processed": 250,
    "percentage": 25,
    "current_batch": 3,
    "total_batches": 10
  },
  "data": [],
  "error": null,
  "metadata": {
    "service": "emoney-[service-name]-service",
    "object_type": "[object_type]",
    "extraction_start": "2024-10-15T10:30:00Z",
    "last_updated": "2024-10-15T10:35:00Z",
    "framework": "Flask|Django|REST API"
  }
}
```

---

## 📁 Service Structure

### Individual Flask Services Structure
Generated using `python emoney_gen.py` with eMoney Advisor-specific templates:

```
emoney/[ServiceName]/
├── api/
│   ├── __init__.py
│   ├── routes.py
│   └── schemas.py
├── docker/
│   ├── Dockerfile.dev
│   ├── Dockerfile.stage
│   ├── Dockerfile.prod
│   └── docker-compose.yml
├── docs/
│   ├── API-DOCS.md
│   ├── EMONEY-INTEGRATION.md
│   └── SETUP-DOCS.md
├── models/
│   ├── __init__.py
│   ├── emoney_models.py
│   └── database.py
├── services/
│   ├── __init__.py
│   ├── emoney_service.py
│   └── extraction_service.py
├── tests/
│   ├── unit/
│   │   └── test_emoney_service.py
│   ├── integration/
│   │   └── test_emoney_api.py
│   └── fixtures/
│       └── emoney_sample_data.json
├── app.py
├── config.py
├── README.md
├── .env.example
└── .gitignore
```

---

## 🔄 Service Communication & Architecture

### Database Architecture
Each Flask service maintains its own PostgreSQL database:

- **emoney_core_db**: Core service routing and orchestration (Django)
- **emoney_client_db**: Client and relationship data
- **emoney_financial_planning_db**: Financial planning and goal data
- **emoney_account_db**: Account and investment data
- **emoney_asset_db**: Asset and allocation data
- **emoney_spending_db**: Spending and budget data
- **emoney_estate_db**: Estate planning data
- **emoney_retirement_db**: Retirement planning data
- **emoney_insurance_db**: Insurance policy data
- **emoney_tax_db**: Tax planning data
- **emoney_document_db**: Document and vault data
- **emoney_user_db**: User and permission data

**Additional Components:**
- **Redis**: Session storage and caching
- **Message Queue**: RabbitMQ for inter-service communication

### Orchestration Flow
1. **Django Core Service** receives requests and routes to appropriate Flask services
2. **Flask Services** extract data from eMoney Advisor APIs independently
3. **Mock Server** provides test data during development

---

## 🐳 Docker Configuration

### Development Environment
```bash
# Start all services in development mode
docker-compose -f docker-compose.dev.yml up -d

# Start specific service group
docker-compose -f docker-compose.dev.yml up -d emoney-core-service-dev emoney-client-service-dev
```

### Production Environment
```bash
# Start all services in production mode
docker-compose -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale emoney-client-service-prod=3
```

---

## 🔒 Security & Authentication

### eMoney Advisor API Authentication
- **OAuth2**: API Key + Secret Authentication
- **Rate Limiting**: Respect eMoney Advisor API rate limits
- **Retry Logic**: Exponential backoff for failed requests

### Inter-Service Security
- **JWT Tokens**: Secure communication between services
- **TLS Encryption**: All service-to-service communication encrypted
- **Network Isolation**: Services isolated in Docker networks

---

## 📊 Monitoring & Health Checks

### Service Health Response
```json
{
  "service": "emoney-[service-name]-service",
  "status": "healthy",
  "timestamp": "2024-10-28T14:30:00Z",
  "version": "1.0.0",
  "framework": "Flask|Django",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "emoney_api_connectivity": "healthy"
  }
}
```