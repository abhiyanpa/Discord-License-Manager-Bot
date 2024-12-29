import json
import os
import logging
from datetime import datetime

logger = logging.getLogger('storage')

class JsonStorage:
    def __init__(self):
        self.filename = 'licenses.json'
        self.data = self._load_data()

    def _load_data(self):
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading JSON data: {str(e)}")
            return {}

    def _save_data(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=4, default=str)
        except Exception as e:
            logger.error(f"Error saving JSON data: {str(e)}")
            raise

    def test_connection(self):
        try:
            self._save_data()
            return True
        except Exception as e:
            logger.error(f"Storage test failed: {str(e)}")
            raise

    def get_user_license(self, user_id: int):
        str_id = str(user_id)
        if str_id in self.data:
            return (
                user_id,
                self.data[str_id]['license_key'],
                self.data[str_id]['created_at'],
                self.data[str_id]['expires_at'],
                self.data[str_id]['license_id']  # Added license_id
            )
        return None

    def add_user_license(self, user_id: int, license_key: str, license_id: int, expires_at: datetime):
        self.data[str(user_id)] = {
            'license_key': license_key,
            'license_id': license_id,  # Added license_id
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        self._save_data()

    def delete_user_license(self, user_id: int):
        str_id = str(user_id)
        if str_id in self.data:
            del self.data[str_id]
            self._save_data()
