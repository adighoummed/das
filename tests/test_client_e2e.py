import os
import pytest
import time
import threading
import requests
from app.main import app
from app.client import APIClient

TEST_DB = "./test_client_e2e.db"
os.environ['DATABASE_URL'] = "sqlite:///%s" % TEST_DB


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Clean up test database file after tests run
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def start_server():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")


def wait_for_server(url, timeout=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.2)
    return False


def test_client_end_to_end():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    assert wait_for_server("http://127.0.0.1:8001/health"), "Server did not start"
    client = APIClient(base_url="http://127.0.0.1:8001", username="admin", password="admin")
    health = client.health_check()
    assert health.get("status") == "OK"
    users = client.list_users()
    assert users == []
    user_data = {"name": "ronaldinho", "address": "New York", "phone": "0523333333", "national_id": "123456782"}
    created = client.create_user(**user_data)
    assert created["name"] == user_data["name"]
    uid = created["id"]
    fetched = client.get_user(uid)
    assert fetched["id"] == uid
    assert fetched["phone"] == user_data["phone"]
    users = client.list_users()
    assert uid in users
    assert client.get_user(99999) is None
