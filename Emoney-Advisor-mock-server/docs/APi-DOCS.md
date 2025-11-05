# eMoney Advisor GET-Only Endpoints & Entity Types (Data Extraction)

**Purpose:**  
This document provides a concise reference to the eMoney Advisor API endpoints for data extraction. It is intended to help developers and integrators quickly identify which GET-only endpoints and entity types are available for use, ensuring reliable access to client information, financial plans, assets, and other wealth management data. Use this guide to streamline integration, reporting, and compliance workflows with eMoney Advisor.

## 🔍 Core GET Endpoints

### Authentication
```
JWT-based authentication with X.509 certificates
POST to https://signin-externalbeta2.emaplan.com/connect/token (Test)
POST to https://signin.emaplan.com/connect/token (Production)
```

### Base URL: 
```
Not publicly disclosed - provided to API clients after authentication setup
```

### Users & Clients
```
GET    /users                              # List all users
GET    /users/{userId}                     # Get specific user
GET    /clients                            # List all clients
GET    /clients/{clientId}                 # Get specific client
GET    /clients/{clientId}/spouse          # Get client spouse information
GET    /clients/{clientId}/plans           # Get client plans
```

### Plans & Financial Data
```
GET    /clients/{clientId}/plans/{planId}              # Get specific plan
GET    /clients/{clientId}/plans/{planId}/assets       # Get plan assets
GET    /clients/{clientId}/plans/{planId}/liabilities  # Get plan liabilities
GET    /clients/{clientId}/plans/{planId}/income       # Get plan income
GET    /clients/{clientId}/plans/{planId}/expenses     # Get plan expenses
GET    /clients/{clientId}/plans/{planId}/monte-carlo  # Get probability of success
```

### Goals & Projections
```
GET    /clients/{clientId}/plans/{planId}/goals             # Get plan goals
GET    /clients/{clientId}/plans/{planId}/net-worth         # Get client net worth
GET    /clients/{clientId}/plans/{planId}/projection        # Get plan projections
```

### Documents & Communication
```
GET    /clients/{clientId}/vault                   # Get client vault documents
GET    /clients/{clientId}/vault/{documentId}      # Get specific vault document
GET    /clients/{clientId}/notes                   # Get client notes
GET    /clients/{clientId}/tasks                   # Get client tasks
GET    /alerts                                     # Get alerts
```

### Administration & Portal Access
```
GET    /logons                                     # Get all portal logon details
GET    /logons/{logonId}                           # Get specific portal logon
GET    /clients/{clientId}/logons                  # Get client portal logon
```

## 📊 Entity Types for Data Extraction

### User & Client Management
- **User** - Advisor, assistant, planner, manager, compliance, and investment specialist users
- **Client** - End-investor client details
- **Spouse** - Client spouse information
- **Logon** - Portal access credentials

### Financial Data
- **Asset** - Client asset information (bank accounts, investments, property, etc.)
- **Liability** - Client liabilities and debts
- **Income** - Client income streams
- **Expense** - Client expenses and outflows
- **NetWorth** - Calculated net worth figures

### Planning Data
- **Plan** - Financial plans (Base Facts, Advanced Planning Scenarios, What-Ifs)
- **Goal** - Client financial goals and objectives
- **MonteCarlo** - Probability of success calculations
- **Projection** - Financial projections and forecasts

### Document & Communication
- **VaultDocument** - Documents stored in the client vault
- **Note** - Client-related notes
- **Task** - Client-related tasks and to-dos
- **Alert** - System and client alerts

## 🎯 Essential GET Queries

### Get All Users
```
GET /users
```

### Get All Clients
```
GET /clients
```

### Get Specific Client
```
GET /clients/{clientId}
```

### Get Client Plans
```
GET /clients/{clientId}/plans
```

### Get Plan Details
```
GET /clients/{clientId}/plans/{planId}
```

### Get Client Assets
```
GET /clients/{clientId}/plans/{planId}/assets
```

### Get Client Goals
```
GET /clients/{clientId}/plans/{planId}/goals
```

### Get Monte Carlo Analysis
```
GET /clients/{clientId}/plans/{planId}/monte-carlo
```

### Get Client Vault Documents
```
GET /clients/{clientId}/vault
```

## 📈 Data Analytics Queries

### Client Financial Overview
```
GET /clients/{clientId}/plans/{planId}                  # Plan overview
GET /clients/{clientId}/plans/{planId}/net-worth        # Net worth calculation
GET /clients/{clientId}/plans/{planId}/monte-carlo      # Success probability
```

### Asset & Liability Analysis
```
GET /clients/{clientId}/plans/{planId}/assets          # All client assets
GET /clients/{clientId}/plans/{planId}/liabilities     # All client liabilities
```

### Income & Expense Analysis
```
GET /clients/{clientId}/plans/{planId}/income          # All income sources
GET /clients/{clientId}/plans/{planId}/expenses        # All expenses
```

### Goal Analysis
```
GET /clients/{clientId}/plans/{planId}/goals           # All client goals
GET /clients/{clientId}/plans/{planId}/expenses?isGoal=true  # Expenses tagged as goals
```

## 🔄 Complex Data Extraction

### Complete Client Financial Overview
```
GET /clients/{clientId}                               # Get client details
GET /clients/{clientId}/plans                         # Get all client plans
GET /clients/{clientId}/plans/{planId}/assets         # Get assets
GET /clients/{clientId}/plans/{planId}/liabilities    # Get liabilities
GET /clients/{clientId}/plans/{planId}/income         # Get income
GET /clients/{clientId}/plans/{planId}/expenses       # Get expenses
GET /clients/{clientId}/plans/{planId}/net-worth      # Get net worth
```

### Goal-Based Planning Analysis
```
GET /clients/{clientId}/plans/{planId}/goals          # Get all goals
GET /clients/{clientId}/plans/{planId}/monte-carlo    # Get success probability
GET /clients/{clientId}/plans/{planId}/projection     # Get future projections
```

### Document Management
```
GET /clients/{clientId}/vault                         # Get all vault documents
GET /clients/{clientId}/notes                         # Get all client notes
GET /clients/{clientId}/tasks                         # Get all client tasks
```

## 📋 Required Headers for All Requests
```
Headers:
  Authorization: Bearer {access_token}             # JWT token
  Content-Type: application/json                   # Request format
  Accept: application/json                         # Response format
```

## 💡 Quick Data Extraction Examples

### Get All Clients
```
curl -X GET "https://[base-url]/clients" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json"
```

### Get Client Plans
```
curl -X GET "https://[base-url]/clients/{clientId}/plans" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json"
```

### Get Client Assets
```
curl -X GET "https://[base-url]/clients/{clientId}/plans/{planId}/assets" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json"
```

### Get Monte Carlo Analysis
```
curl -X GET "https://[base-url]/clients/{clientId}/plans/{planId}/monte-carlo" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json"
```

## 📊 Response Format Examples

### Client Response
```json
{
  "clientId": "12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "johndoe@example.com",
  "phone": "555-123-4567",
  "maritalStatus": "Married",
  "previousMarriages": false,
  "dateOfBirth": "1975-06-15",
  "owningAdvisor": "67890",
  "externalId": "CRM-123456"
}
```

### Asset Response
```json
{
  "assets": [
    {
      "id": "asset-001",
      "name": "Primary Residence",
      "type": "Real Estate",
      "value": 750000,
      "basis": 500000,
      "growthRate": 0.03,
      "ownership": "Joint"
    },
    {
      "id": "asset-002",
      "name": "401(k)",
      "type": "Retirement",
      "value": 450000,
      "basis": 350000,
      "growthRate": 0.06,
      "ownership": "Client"
    }
  ],
  "totalValue": 1200000
}
```

### Goal Response
```json
{
  "goals": [
    {
      "id": "goal-001",
      "name": "Retirement",
      "startDate": "2040-01-01",
      "endDate": "2065-01-01",
      "amount": 100000,
      "frequency": "Annual",
      "inflationRate": 0.025,
      "priority": "High"
    },
    {
      "id": "goal-002",
      "name": "College Education",
      "startDate": "2030-08-01",
      "endDate": "2034-05-31",
      "amount": 35000,
      "frequency": "Annual",
      "inflationRate": 0.04,
      "priority": "Medium"
    }
  ]
}
```

## 🔧 Authentication Setup

### JWT Token Generation Example (JavaScript)
```javascript
const crypto = require('crypto');
const fs = require('fs');
const axios = require('axios');

// Load private key from PFX file (requires password)
const pfxData = fs.readFileSync('certificate.pfx');
const privateKey = crypto.createPrivateKey({
  pfx: pfxData,
  passphrase: 'your-password'
});

// Create JWT header
const header = {
  alg: 'RS256',
  typ: 'JWT'
};

// Create JWT payload
const payload = {
  iss: 'YOUR_CLIENT_ID',
  sub: 'YOUR_CLIENT_ID',
  aud: 'https://signin-externalbeta2.emaplan.com/connect/token',
  exp: Math.floor(Date.now() / 1000) + (60 * 60), // 1 hour from now
  jti: crypto.randomUUID()
};

// Encode header and payload
const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');

// Create signature
const dataToSign = `${encodedHeader}.${encodedPayload}`;
const signature = crypto.sign('sha256', Buffer.from(dataToSign), privateKey);
const encodedSignature = Buffer.from(signature).toString('base64url');

// Create complete JWT
const jwt = `${encodedHeader}.${encodedPayload}.${encodedSignature}`;

// Request token
async function getAccessToken() {
  const tokenUrl = 'https://signin-externalbeta2.emaplan.com/connect/token';
  const params = new URLSearchParams();
  params.append('client_assertion_type', 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer');
  params.append('client_assertion', jwt);
  params.append('grant_type', 'client_credentials');
  params.append('scope', 'API');

  try {
    const response = await axios.post(tokenUrl, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data.access_token;
  } catch (error) {
    console.error('Error getting access token:', error);
  }
}

// Use the token to call an API
async function getClients() {
  const token = await getAccessToken();
  const response = await axios.get('https://[base-url]/clients', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json'
    }
  });
  return response.data;
}
```

## ⚡ Key Points for Data Extraction

- **Authentication**: JWT-based with X.509 certificates for security
- **Response Format**: JSON
- **Rate Limits**: 60 concurrent calls for most endpoints; 250 calls per hour for Monte Carlo endpoints
- **API Structure**: Hierarchical client → plans → financial data structure
- **Plan Types**: Base Facts, Advanced Planning Scenarios, What-Ifs
- **Data Categories**: Assets, liabilities, income, expenses, goals, net worth
- **Monte Carlo Analysis**: Industry-standard probability of success calculations
- **Document Management**: Client vault for document storage and retrieval

Perfect for extracting client data, financial plans, and portfolio information for wealth management, compliance, and reporting purposes!

## 🚨 Important Note

This documentation covers expected eMoney Advisor API endpoints based on available information. For complete and official API documentation:

- Contact: Client Services or Sales team at eMoney Advisor
- Developer Portal: https://developer.emoneyadvisor.com/
- API Access Request: https://explore.emoneyadvisor.com/apis