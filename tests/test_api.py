import os

TEST_DB = "./test_api.db"

os.environ['DATABASE_URL'] = "sqlite:///%s" % TEST_DB
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# @pytest.fixture(scope="session", autouse=True)
# def setup_test_environment():
#     # Clean up test database file after tests run
#     if os.path.exists(TEST_DB):
#         os.remove(TEST_DB)

def get_auth_header():
    resp = client.post("/token", data={"username": "admin", "password": "admin"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "OK"


def test_auth_required():
    resp = client.get("/users")
    assert resp.status_code == 401
    resp = client.post("/token", data={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401
    assert "Incorrect username or password" in resp.json().get("detail", "")


def test_user_crud_flow():
    headers = get_auth_header()
    resp = client.get("/users", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []
    new_user = {"name": "Test User", "address": "Test Address", "phone": "0521234567", "national_id": "123456782"}
    resp = client.post("/users", json=new_user, headers=headers)
    assert resp.status_code == 201
    created = resp.json()
    assert "id" in created
    user_id = created["id"]
    assert created["name"] == new_user["name"]
    resp2 = client.post("/users", json=new_user, headers=headers)
    assert resp2.status_code == 400
    assert "already exists" in resp2.json().get("detail", "")
    resp = client.get(f"/users/{user_id}", headers=headers)
    assert resp.status_code == 200
    fetched = resp.json()
    assert fetched["id"] == user_id
    assert fetched["national_id"] == new_user["national_id"]
    resp = client.get("/users/999", headers=headers)
    assert resp.status_code == 404
    resp = client.get("/users", headers=headers)
    assert resp.status_code == 200
    ids = resp.json()
    assert user_id in ids


@pytest.mark.parametrize("invalid_user", [
    {"name": "A", "address": "Addr", "phone": "0521234567", "national_id": "111111111"},
    {"name": "A", "address": "Address", "phone": "12345", "national_id": "123456782"},
    {"address": "Address", "phone": "0521234567", "national_id": "123456782"},
])
def test_input_validation(invalid_user):
    headers = get_auth_header()
    resp = client.post("/users", json=invalid_user, headers=headers)
    assert resp.status_code == 422
    detail = resp.json().get("detail")
    assert detail is not None
    expected_errors = ["Invalid Israeli ID", "Invalid phone number format", "field required"]
    error_messages = " ".join(str(d.get("msg")) for d in detail)
    assert any(err in error_messages for err in expected_errors)
