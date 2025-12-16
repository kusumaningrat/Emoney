# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY mock_config.py .
COPY mock_server.py .

# Expose port
EXPOSE 5001

# Environment variables with defaults
ENV MOCK_HOST=0.0.0.0
ENV MOCK_PORT=5001
ENV MOCK_DEBUG=false
ENV TOTAL_MOCK_USERS=1000

# Run mock server
CMD ["python", "mock_server.py"]