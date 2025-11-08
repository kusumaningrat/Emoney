FROM python:3.11-slim

WORKDIR /app

# Install only the essential PostgreSQL dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for API
EXPOSE 6820

# Start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "6820"]