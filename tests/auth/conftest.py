import pytest
from starlette.testclient import TestClient


@pytest.fixture
def default_user(client: TestClient):
    resp = client.post(
        "/users",
        json={
            "username": "test_user",
            "password": "123Aa!",
        },
    )
    return resp.json()["details"]
