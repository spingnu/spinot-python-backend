from __future__ import annotations

import requests

from app.config import Config


class AIAPIClient:
    def __init__(self, base_url, api_key=None):
        """
        Initializes the API client with a base URL and an optional API key.

        :param base_url: The base URL of the API.
        :param api_key: Optional API key for authentication.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.version = "/api/v1"

    def _get(self, endpoint, params=None):
        """
        Internal method to make a GET request.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data=None, json_data=None):
        """
        Internal method to make a POST request.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if json_data:
            headers["Content-Type"] = "application/json"

        response = requests.post(url, headers=headers, data=data, json=json_data)
        response.raise_for_status()
        return response.json()

    def health_check(self):
        """
        Check the health of the AI server.

        :return: The health status of the AI server.
        """
        endpoint = "health"
        return self._get(endpoint)


ai_api_client = AIAPIClient(Config.AI_SERVER_URL)
