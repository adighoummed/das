import requests
import logging

class APIClient:
    def __init__(self, base_url="http://localhost:8000", username=None, password=None, token=None):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger("client")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.session = requests.Session()
        if token:
            self.token = token
        elif username and password:
            self.logger.info("Authenticating with server at %s", self.base_url)
            resp = self.session.post(f"{self.base_url}/token", data={"username": username, "password": password})
            if resp.status_code != 200:
                raise Exception(f"Authentication failed: {resp.status_code} {resp.text}")
            data = resp.json()
            self.token = data.get("access_token")
            if not self.token:
                raise Exception("Failed to obtain access token")
        else:
            raise ValueError("Must provide either token or username/password")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.logger.info("APIClient initialized (base_url=%s)", self.base_url)

    def create_user(self, name: str, phone: str, address: str, national_id: str):
        payload = {"name": name, "phone": phone, "address": address, "national_id": national_id}
        self.logger.info("POST %s/users - Payload: %s", self.base_url, payload)
        resp = self.session.post(f"{self.base_url}/users", json=payload)
        self.logger.info("Response: %d %s", resp.status_code, resp.text)
        if resp.status_code != 201:
            raise Exception(f"Failed to create user: {resp.status_code} {resp.text}")
        return resp.json()

    def get_user(self, user_id: int):
        self.logger.info("GET %s/users/%s", self.base_url, user_id)
        resp = self.session.get(f"{self.base_url}/users/{user_id}")
        self.logger.info("Response: %d %s", resp.status_code, resp.text)
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise Exception(f"Failed to get user: {resp.status_code} {resp.text}")
        return resp.json()

    def list_users(self):
        self.logger.info("GET %s/users", self.base_url)
        resp = self.session.get(f"{self.base_url}/users")
        self.logger.info("Response: %d %s", resp.status_code, resp.text)
        if resp.status_code != 200:
            raise Exception(f"Failed to list users: {resp.status_code} {resp.text}")
        return resp.json()

    def health_check(self):
        self.logger.info("GET %s/health", self.base_url)
        resp = self.session.get(f"{self.base_url}/health")
        self.logger.info("Response: %d %s", resp.status_code, resp.text)
        if resp.status_code != 200:
            raise Exception(f"Health check failed: {resp.status_code} {resp.text}")
        return resp.json()
