"""Implementasi repository in-memory untuk demo dan pengujian lokal."""
from dataclasses import replace
from threading import RLock
from app.domain.product import Product
from app.repositories.interfaces import ProductRepository

class InMemoryProductRepository(ProductRepository):
    """Penyimpanan sederhana; data hilang ketika proses aplikasi berhenti."""
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._next_id = 1
        self._lock = RLock()

    def list_all(self) -> list[Product]:
        with self._lock:
            return sorted(self._products.values(), key=lambda item: item.id)

    def get_by_id(self, product_id: int) -> Product | None:
        with self._lock:
            return self._products.get(product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        normalized = sku.casefold()
        with self._lock:
            return next((p for p in self._products.values() if p.sku.casefold() == normalized), None)

    def add(self, product: Product) -> Product:
        with self._lock:
            saved = replace(product, id=self._next_id)
            self._products[saved.id] = saved
            self._next_id += 1
            return saved

    def update(self, product: Product) -> Product:
        with self._lock:
            if product.id not in self._products:
                raise KeyError(f"Produk dengan ID {product.id} tidak ditemukan.")
            self._products[product.id] = product
            return product

    def delete(self, product_id: int) -> bool:
        with self._lock:
            return self._products.pop(product_id, None) is not None
