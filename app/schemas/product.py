"""Kontrak request/response API menggunakan Pydantic V2."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class ProductCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    sku: str = Field(min_length=3, max_length=30, description="Kode unik produk")
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0, allow_inf_nan=False, description="Harga harus lebih dari nol")
    stock: int = Field(ge=0, description="Stok tidak boleh negatif")
    category: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("sku", mode="before")
    @classmethod
    def normalize_sku(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
            if not all(ch.isalnum() or ch in "_-" for ch in value):
                raise ValueError("SKU hanya boleh berisi huruf, angka, tanda hubung, dan garis bawah.")
        return value

    @field_validator("name", "category", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    sku: str | None = Field(default=None, min_length=3, max_length=30)
    name: str | None = Field(default=None, min_length=2, max_length=100)
    price: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("sku", mode="before")
    @classmethod
    def normalize_sku(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip().upper()
            if not all(ch.isalnum() or ch in "_-" for ch in value):
                raise ValueError("SKU hanya boleh berisi huruf, angka, tanda hubung, dan garis bawah.")
        return value

    @field_validator("name", "category", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("sku", "name", "price", "stock", "category")
    @classmethod
    def required_update_fields_cannot_be_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("Field ini tidak boleh bernilai null; hilangkan field jika tidak ingin mengubahnya.")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @model_validator(mode="after")
    def require_at_least_one_change(self) -> "ProductUpdate":
        if not self.model_fields_set:
            raise ValueError("Minimal satu field harus dikirim untuk pembaruan.")
        return self

class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    price: float
    stock: int
    category: str
    description: str | None
    created_at: datetime
