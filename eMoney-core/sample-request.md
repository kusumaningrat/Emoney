<!-- Client Scan -->
.

{
  "scan_type": "client",
  "entity_types": [ 
      "contact",
      "client",
      "prospect",
      "lead",
      "family_account",
      "household"]
    ,
  "organizationId": "org-12345",
  "auth": {
    "apiKey": "your-redtail-api-key-here",
    "username": "your-username",
    "password": "your-password"
  },
  "filters": {
    "dateRange": {
      "startDate": "2024-01-01",
      "endDate": "2024-12-31"
    }
  }
}

{
  "scan_type": "client",
  "entity_types": [ "contact"],
  "organizationId": "org-12345",
  "auth": {
    "apiKey": "your-redtail-api-key-here",
    "username": "your-username",
    "password": "your-password"
  },
  "filters": {
    "dateRange": {
      "startDate": "2024-01-01",
      "endDate": "2024-12-31"
    }
  }
}