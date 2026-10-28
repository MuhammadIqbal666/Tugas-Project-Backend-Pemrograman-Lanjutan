from tests.conftest import ADMIN_KEY, STAFF_KEY


def test_root_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_products_is_empty_initially(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert response.json() == []


def test_create_product_by_staff_returns_201(client, product_payload):
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["sku"] == "KB-001"


def test_create_product_by_admin(client, product_payload):
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": ADMIN_KEY})
    assert response.status_code == 201


def test_create_normalizes_sku_and_text(client, product_payload):
    product_payload.update({"sku": " mouse_01 ", "name": " Mouse Wireless ", "category": " Elektronik "})
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "MOUSE_01"
    assert data["name"] == "Mouse Wireless"
    assert data["category"] == "Elektronik"


def test_create_product_without_api_key_returns_401(client, product_payload):
    response = client.post("/api/v1/products", json=product_payload)
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_create_product_with_invalid_api_key_returns_401(client, product_payload):
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_create_duplicate_sku_returns_409(client, create_product, product_payload):
    create_product()
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 409
    assert response.json()["code"] == "DUPLICATE_SKU"


def test_create_product_with_zero_price_returns_422(client, product_payload):
    product_payload["price"] = 0
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["path"] == "/api/v1/products"
    assert response.json()["details"]


def test_create_product_with_negative_stock_returns_422(client, product_payload):
    product_payload["stock"] = -1
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422


def test_create_product_with_bad_sku_returns_422(client, product_payload):
    product_payload["sku"] = "SKU / ONE"
    response = client.post("/api/v1/products", json=product_payload, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422


def test_create_product_with_missing_required_field_returns_422(client):
    response = client.post("/api/v1/products", json={"sku": "KB-009"}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422


def test_get_product_by_id(client, create_product):
    created = create_product()
    response = client.get(f"/api/v1/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Keyboard Mechanical"


def test_get_nonexistent_product_returns_404(client):
    response = client.get("/api/v1/products/12345")
    assert response.status_code == 404
    assert response.json()["code"] == "PRODUCT_NOT_FOUND"


def test_list_products_returns_created_products(client, create_product):
    create_product()
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_products_by_category_case_insensitive(client, create_product, product_payload):
    create_product()
    another = {**product_payload, "sku": "MON-001", "name": "Monitor", "category": "Elektronik"}
    create_product(another)
    response = client.get("/api/v1/products", params={"category": "elektronik"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Monitor"]


def test_search_products_by_name_or_sku(client, create_product):
    create_product()
    response = client.get("/api/v1/products", params={"q": "keyboard"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_patch_product_only_changes_given_field(client, create_product):
    created = create_product()
    response = client.patch(f"/api/v1/products/{created['id']}", json={"price": 500000}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 200
    assert response.json()["price"] == 500000
    assert response.json()["name"] == "Keyboard Mechanical"
    assert response.json()["stock"] == 10


def test_patch_can_clear_description(client, create_product):
    created = create_product()
    response = client.patch(f"/api/v1/products/{created['id']}", json={"description": None}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 200
    assert response.json()["description"] is None


def test_patch_empty_payload_returns_422(client, create_product):
    created = create_product()
    response = client.patch(f"/api/v1/products/{created['id']}", json={}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422


def test_patch_null_price_returns_422(client, create_product):
    created = create_product()
    response = client.patch(f"/api/v1/products/{created['id']}", json={"price": None}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 422


def test_patch_nonexistent_product_returns_404(client):
    response = client.patch("/api/v1/products/444", json={"name": "New Name"}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 404


def test_patch_duplicate_sku_returns_409(client, create_product, product_payload):
    first = create_product()
    second = create_product({**product_payload, "sku": "MS-002", "name": "Mouse"})
    response = client.patch(f"/api/v1/products/{second['id']}", json={"sku": first["sku"]}, headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 409


def test_patch_requires_authentication(client, create_product):
    created = create_product()
    response = client.patch(f"/api/v1/products/{created['id']}", json={"stock": 5})
    assert response.status_code == 401


def test_delete_by_staff_is_forbidden(client, create_product):
    created = create_product()
    response = client.delete(f"/api/v1/products/{created['id']}", headers={"X-API-Key": STAFF_KEY})
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_delete_by_admin_returns_204_and_removes_product(client, create_product):
    created = create_product()
    response = client.delete(f"/api/v1/products/{created['id']}", headers={"X-API-Key": ADMIN_KEY})
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/v1/products/{created['id']}").status_code == 404


def test_delete_nonexistent_product_returns_404(client):
    response = client.delete("/api/v1/products/789", headers={"X-API-Key": ADMIN_KEY})
    assert response.status_code == 404


def test_delete_requires_api_key(client, create_product):
    created = create_product()
    assert client.delete(f"/api/v1/products/{created['id']}").status_code == 401


def test_invalid_product_id_returns_standard_validation_error(client):
    response = client.get("/api/v1/products/not-an-id")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
