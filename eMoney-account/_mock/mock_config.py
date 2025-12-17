# mock_config.py
import os

# Mock server settings
MOCK_HOST = os.getenv('MOCK_HOST', '0.0.0.0')
MOCK_PORT = int(os.getenv('MOCK_PORT', '5001'))
MOCK_DEBUG = os.getenv('MOCK_DEBUG', 'true').lower() == 'true'

# App info
APP_TITLE = os.getenv('APP_TITLE', 'Mock Data API')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
APP_DESCRIPTION = os.getenv('APP_DESCRIPTION', 'Mock API server for testing')

# Mock data settings
TOTAL_MOCK_USERS = int(os.getenv('TOTAL_MOCK_USERS', '1000'))
DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '100'))
MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '500'))

# Test settings
DEFAULT_TEST_DELAY = float(os.getenv('DEFAULT_TEST_DELAY', '0'))  # seconds

# Faker settings
FAKER_SEED = int(os.getenv('FAKER_SEED', '12345'))  # For consistent test data

# HubSpot-like Rate Limiting (per 10 seconds)
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', '40000'))  # HubSpot default
BURST_LIMIT = int(os.getenv('BURST_LIMIT', '100'))   # Per 10 seconds
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '10'))  # seconds