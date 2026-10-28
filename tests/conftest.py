import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.repositories.in_memory import InMemoryProductRepository

ADMIN_KEY = "admin-test-key"
STAFF_KEY = "staff-test-key"

@pytest.fixture
def repository():
    return InMemoryProductRepository()

@pytest.fixture
def client(repository):
    settings = Settings(admin_api_key=ADMIN_KEY, staff_api_key=STAFF_KEY)
    app = create_app(repository=repository, settings=settings)
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def product_payload():
    return {
        "sku": "KB-001",
        "name": "Keyboard Mechanical",
        "price": 450000,
        "stock": 10,
        "category": "Aksesoris",
        "description": "Keyboard untuk komputer",
    }

@pytest.fixture
def create_product(client, product_payload):
    def _create(payload=None, key=STAFF_KEY):
        response = client.post("/api/v1/products", json=payload or product_payload, headers={"X-API-Key": key})
        assert response.status_code == 201, response.text
        return response.json()
    return _create
