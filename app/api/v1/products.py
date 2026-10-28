"""HTTP routes untuk resource products versi v1."""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Response, status
from app.dependencies import get_product_service, require_admin, require_staff
from app.domain.principal import Principal
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
StaffDep = Annotated[Principal, Depends(require_staff)]
AdminDep = Annotated[Principal, Depends(require_admin)]

@router.get("", response_model=list[ProductRead], summary="Daftar produk")
def list_products(service: ProductServiceDep, category: Annotated[str | None, Query(min_length=2, max_length=50)] = None, q: Annotated[str | None, Query(min_length=1, max_length=100, description="Cari nama, SKU, atau kategori")] = None) -> list[ProductRead]:
    return service.list_products(category=category, q=q)

@router.get("/{product_id}", response_model=ProductRead, summary="Detail produk")
def get_product(product_id: int, service: ProductServiceDep) -> ProductRead:
    return service.get_product(product_id)

@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Tambah produk")
def create_product(payload: ProductCreate, service: ProductServiceDep, _user: StaffDep) -> ProductRead:
    return service.create_product(payload)

@router.patch("/{product_id}", response_model=ProductRead, summary="Perbarui sebagian data produk")
def update_product(product_id: int, payload: ProductUpdate, service: ProductServiceDep, _user: StaffDep) -> ProductRead:
    return service.update_product(product_id, payload)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Hapus produk (admin)")
def delete_product(product_id: int, service: ProductServiceDep, _admin: AdminDep) -> Response:
    service.delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
