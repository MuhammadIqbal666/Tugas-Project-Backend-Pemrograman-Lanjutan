"""Exception bisnis yang bisa dipetakan ke HTTP response."""
class ProductNotFoundError(Exception):
    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(f"Produk dengan ID {product_id} tidak ditemukan.")

class DuplicateSKUError(Exception):
    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"SKU '{sku}' sudah digunakan oleh produk lain.")
