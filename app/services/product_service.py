"""Aturan bisnis produk; hanya bergantung pada abstraksi ProductRepository."""
from dataclasses import replace
from app.domain.product import Product
from app.repositories.interfaces import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.exceptions import DuplicateSKUError, ProductNotFoundError

class ProductService:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def list_products(self, category: str | None = None, q: str | None = None) -> list[Product]:
        products = self._repository.list_all()
        if category:
            target = category.strip().casefold()
            products = [item for item in products if item.category.casefold() == target]
        if q:
            query = q.strip().casefold()
            products = [item for item in products if query in item.name.casefold() or query in item.sku.casefold() or query in item.category.casefold()]
        return products

    def get_product(self, product_id: int) -> Product:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    def create_product(self, payload: ProductCreate) -> Product:
        if self._repository.get_by_sku(payload.sku) is not None:
            raise DuplicateSKUError(payload.sku)
        product = Product(id=0, **payload.model_dump())
        return self._repository.add(product)

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        current = self.get_product(product_id)
        changes = payload.model_dump(exclude_unset=True)
        if "sku" in changes:
            existing = self._repository.get_by_sku(changes["sku"])
            if existing is not None and existing.id != product_id:
                raise DuplicateSKUError(changes["sku"])
        updated = replace(current, **changes)
        try:
            return self._repository.update(updated)
        except KeyError as exc:
            raise ProductNotFoundError(product_id) from exc

    def delete_product(self, product_id: int) -> None:
        self.get_product(product_id)
        if not self._repository.delete(product_id):
            raise ProductNotFoundError(product_id)
