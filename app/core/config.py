"""Konfigurasi aplikasi yang dapat diganti lewat environment variables."""

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "Sistem Manajemen Produk Toko API"
    app_version: str = "1.0.0"
    admin_api_key: str = "admin-demo-key"
    staff_api_key: str = "staff-demo-key"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            admin_api_key=os.getenv("PRODUCT_ADMIN_API_KEY", "admin-demo-key"),
            staff_api_key=os.getenv("PRODUCT_STAFF_API_KEY", "staff-demo-key"),
        )

    def __post_init__(self) -> None:
        if not self.admin_api_key or not self.staff_api_key:
            raise ValueError("API key admin dan staff tidak boleh kosong.")
        if self.admin_api_key == self.staff_api_key:
            raise ValueError("API key admin dan staff harus berbeda.")
