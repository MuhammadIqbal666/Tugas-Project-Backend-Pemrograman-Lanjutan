"""Dependency Injection: repository, service, authentication, dan RBAC."""
import secrets
from typing import Annotated
from fastapi import Depends, Header, HTTPException, Request, status
from app.domain.principal import Principal
from app.repositories.interfaces import ProductRepository
from app.services.product_service import ProductService

def get_product_repository(request: Request) -> ProductRepository:
    return request.app.state.product_repository

def get_product_service(repository: Annotated[ProductRepository, Depends(get_product_repository)]) -> ProductService:
    return ProductService(repository)

def get_current_user(request: Request, x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> Principal:
    settings = request.app.state.settings
    if x_api_key is not None and secrets.compare_digest(x_api_key, settings.admin_api_key):
        return Principal(role="ADMIN")
    if x_api_key is not None and secrets.compare_digest(x_api_key, settings.staff_api_key):
        return Principal(role="STAFF")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key tidak ada atau tidak valid.", headers={"WWW-Authenticate": "ApiKey"})

def require_staff(current_user: Annotated[Principal, Depends(get_current_user)]) -> Principal:
    if current_user.role not in ("ADMIN", "STAFF"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses membutuhkan role STAFF atau ADMIN.")
    return current_user

def require_admin(current_user: Annotated[Principal, Depends(get_current_user)]) -> Principal:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses hanya untuk ADMIN.")
    return current_user
