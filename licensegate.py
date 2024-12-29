import aiohttp
import logging
from datetime import datetime, timedelta
from config import (
    LICENSEGATE_API_KEY, 
    LICENSEGATE_BASE_URL,
    LICENSE_DURATION_DAYS,
    LICENSE_IP_LIMIT,
    LICENSE_VALIDATION_LIMIT,
    LICENSE_REPLENISH_AMOUNT
)

logger = logging.getLogger('licensegate')

class LicenseGateError(Exception):
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

class LicenseGateAPI:
    def __init__(self):
        self.base_url = LICENSEGATE_BASE_URL.rstrip('/') + "/admin/licenses"
        self.headers = {
            "Authorization": LICENSEGATE_API_KEY,
            "Content-Type": "application/json"
        }
        logger.debug(f"Initialized LicenseGateAPI with base URL: {self.base_url}")

    async def create_license(self, username: str):
        try:
            async with aiohttp.ClientSession() as session:
                expiration_date = datetime.now() + timedelta(days=LICENSE_DURATION_DAYS)
                payload = {
                    "active": True,
                    "name": f"{username}/CSpawner",
                    "notes": "Created by Discord bot",
                    "ipLimit": int(LICENSE_IP_LIMIT),
                    "licenseScope": "",
                    "expirationDate": expiration_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    "validationPoints": float(LICENSE_VALIDATION_LIMIT),
                    "validationLimit": int(LICENSE_VALIDATION_LIMIT),
                    "replenishAmount": int(LICENSE_REPLENISH_AMOUNT),
                    "replenishInterval": "DAY"
                }
                logger.debug(f"Creating license with payload: {payload}")
                
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    ssl=True
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"API Request Headers: {self.headers}")
                    logger.debug(f"API Request Payload: {payload}")
                    logger.debug(f"API Response [{response.status}]: {response_text}")
                    
                    if response.status == 201:
                        response_data = await response.json()
                        if 'licenseKey' not in response_data:
                            raise LicenseGateError(
                                "Missing licenseKey in response",
                                status_code=response.status,
                                response=response_text
                            )
                        return response_data
                    
                    raise LicenseGateError(
                        f"API Error: {response_text}",
                        status_code=response.status,
                        response=response_text
                    )
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise LicenseGateError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def delete_license(self, license_id: int):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.base_url}/{license_id}",
                    headers=self.headers
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"API Response [{response.status}]: {response_text}")
                    
                    if response.status not in (200, 204):
                        raise LicenseGateError(
                            f"Failed to delete license: {response_text}",
                            status_code=response.status,
                            response=response_text
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {str(e)}")
            raise LicenseGateError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
