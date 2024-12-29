import os
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse

logger = logging.getLogger('config')

load_dotenv()

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def check_config():
    logger.debug("Starting configuration validation...")
    required_vars = ['DISCORD_TOKEN', 'LICENSE_CHANNEL_ID', 'LICENSEGATE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    if not validate_url(LICENSEGATE_BASE_URL):
        raise ValueError(f"Invalid LICENSEGATE_BASE_URL: {LICENSEGATE_BASE_URL}")

    if not isinstance(LICENSE_IP_LIMIT, int):
        raise ValueError("LICENSE_IP_LIMIT must be an integer")
    if not isinstance(LICENSE_VALIDATION_LIMIT, (int, float)):
        raise ValueError("LICENSE_VALIDATION_LIMIT must be a number")
    if not isinstance(LICENSE_REPLENISH_AMOUNT, int):
        raise ValueError("LICENSE_REPLENISH_AMOUNT must be an integer")
    if LICENSE_REPLENISH_INTERVAL not in ["TEN_SECONDS", "MINUTE", "HOUR", "DAY"]:
        raise ValueError("LICENSE_REPLENISH_INTERVAL must be one of: TEN_SECONDS, MINUTE, HOUR, DAY")
    
    logger.debug("Configuration validation completed successfully")

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN is required")

try:
    LICENSE_CHANNEL_ID = int(os.getenv('LICENSE_CHANNEL_ID'))
except (TypeError, ValueError):
    raise ValueError("LICENSE_CHANNEL_ID must be a valid integer")

LICENSEGATE_API_KEY = os.getenv('LICENSEGATE_API_KEY')
if not LICENSEGATE_API_KEY:
    raise ValueError("LICENSEGATE_API_KEY is required")

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL is required")

LICENSEGATE_BASE_URL = "https://api.licensegate.io"  # Update with your actual LicenseGate server URL

LICENSEGATE_API_VERSION = "1.0.1"

# License configuration
LICENSE_DURATION_DAYS = 90
LICENSE_IP_LIMIT = 2
LICENSE_VALIDATION_LIMIT = 1000
LICENSE_REPLENISH_AMOUNT = 100
LICENSE_REPLENISH_INTERVAL = "DAY"

# Role configuration
GENERATE_ROLE_ID = 0  # Replace with your role ID
