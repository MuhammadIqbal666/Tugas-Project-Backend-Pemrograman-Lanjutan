"""Entitas domain Product; tidak bergantung pada FastAPI atau database."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    sku: str
    name: str
    price: float
    stock: int
    category: str
    description: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
