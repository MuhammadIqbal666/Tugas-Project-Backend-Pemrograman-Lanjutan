import pytest
from app.repositories.in_memory import InMemoryProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.exceptions import DuplicateSKUError, ProductNotFoundError
from app.services.product_service import ProductService

@pytest.fixture
def service():
    return ProductService(InMemoryProductRepository())

def create_payload(**overrides):
    data = {"sku": "BK-001", "name": "Buku Catatan", "price": 12000, "stock": 20, "category": "Alat Tulis", "description": "Buku tulis"}
    data.update(overrides)
    return ProductCreate(**data)

def test_create_product_assigns_id(service):
    product = service.create_product(create_payload())
    assert product.id == 1
    assert product.sku == "BK-001"

def test_create_duplicate_sku_is_rejected_case_insensitively(service):
    service.create_product(create_payload())
    with pytest.raises(DuplicateSKUError):
        service.create_product(create_payload(sku="bk-001"))

def test_get_product_not_found_raises_domain_error(service):
    with pytest.raises(ProductNotFoundError):
        service.get_product(10)

def test_update_product_preserves_unspecified_fields(service):
    product = service.create_product(create_payload())
    updated = service.update_product(product.id, ProductUpdate(stock=8))
    assert updated.stock == 8
    assert updated.name == "Buku Catatan"
    assert updated.price == 12000

def test_update_product_can_set_description_to_none(service):
    product = service.create_product(create_payload())
    updated = service.update_product(product.id, ProductUpdate(description=None))
    assert updated.description is None

def test_update_product_rejects_duplicate_sku(service):
    first = service.create_product(create_payload())
    second = service.create_product(create_payload(sku="PEN-001", name="Pulpen"))
    with pytest.raises(DuplicateSKUError):
        service.update_product(second.id, ProductUpdate(sku=first.sku))

def test_update_unknown_product_raises_not_found(service):
    with pytest.raises(ProductNotFoundError):
        service.update_product(999, ProductUpdate(name="Baru"))

def test_delete_product_removes_item(service):
    product = service.create_product(create_payload())
    service.delete_product(product.id)
    assert service.list_products() == []

def test_delete_unknown_product_raises_not_found(service):
    with pytest.raises(ProductNotFoundError):
        service.delete_product(333)

def test_filter_by_category_is_case_insensitive(service):
    service.create_product(create_payload())
    service.create_product(create_payload(sku="MUG-01", name="Mug", category="Minuman"))
    items = service.list_products(category="alat tulis")
    assert len(items) == 1
    assert items[0].name == "Buku Catatan"

def test_search_matches_sku(service):
    service.create_product(create_payload())
    assert len(service.list_products(q="bk-00")) == 1

def test_search_matches_category(service):
    service.create_product(create_payload())
    assert len(service.list_products(q="tulis")) == 1
