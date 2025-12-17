# Service Orchestrator

A FastAPI-based orchestration service for managing identity and other services.

## Features

- Service connection management
- Identity scan orchestration
- Status monitoring and health checks
- API key authentication

## Architecture

The Service Orchestrator provides a unified API for managing and orchestrating various microservices. It acts as a central hub for:

1. **Service Discovery and Registration**: Allows dynamic registration of services
2. **Identity Scan Coordination**: Manages scan operations across identity services
3. **Status Monitoring**: Tracks health and status of all connected services

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository
```bash
   git clone https://github.com/your-org/service-orchestrator.git
   cd redtail-core
```

2. Create a virtual environment
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Set up environment variables
```bash
   cp .env.example .env
   # Edit .env with your configuration
```

5. Initialize the database
```bash
   python scripts/init_db.py
```

### Running the Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or using the convenience script:
```bash
python -m app.main
```

### Docker Deployment

Build and run with Docker Compose:
```bash
docker-compose up -d
```

## API Documentation

When the service is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Usage Examples

### Connecting a Service
```bash
curl -X POST "http://localhost:8000/api/v1/services/connect" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key_here" \
     -d '{
         "name": "Identity Service",
         "url": "http://identity-service:4601",
         "service_type": "identity",
         "description": "Redtail Identity Service"
     }'
```

### Starting a Scan
```bash
curl -X POST "http://localhost:8000/api/v1/scan/start" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_api_key_here" \
     -d '{
         "service_id": "your_service_id",
         "parameters": {
             "batch_size": 100
         }
     }'
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
