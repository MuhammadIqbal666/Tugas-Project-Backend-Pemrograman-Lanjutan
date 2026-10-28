"""Application factory, router registration, dan centralized error handling."""
import logging
from typing import Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.products import router as products_router
from app.core.config import Settings
from app.repositories.in_memory import InMemoryProductRepository
from app.repositories.interfaces import ProductRepository
from app.services.exceptions import DuplicateSKUError, ProductNotFoundError

logger = logging.getLogger(__name__)

def _error_payload(code: str, message: str, path: str, details: Any = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "error", "code": code, "message": message, "path": path}
    if details is not None:
        payload["details"] = details
    return payload

def create_app(repository: ProductRepository | None = None, settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings.from_env()
    app = FastAPI(title=app_settings.app_name, version=app_settings.app_version, description="REST API modular untuk mengelola produk toko; dokumentasi dibuat otomatis oleh OpenAPI.")
    app.state.product_repository = repository or InMemoryProductRepository()
    app.state.settings = app_settings

    @app.get("/", tags=["Health"], summary="Status API")
    def root() -> dict[str, str]:
        return {"service": "Sistem Manajemen Produk Toko API", "status": "running", "version": app.version}

    @app.get("/health", tags=["Health"], summary="Health check")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"field": " -> ".join(str(part) for part in error.get("loc", ())), "message": error.get("msg", "Nilai tidak valid.")} for error in exc.errors()]
        return JSONResponse(status_code=422, content=_error_payload("VALIDATION_ERROR", "Data request tidak valid.", request.url.path, details))

    @app.exception_handler(ProductNotFoundError)
    async def product_not_found_handler(request: Request, exc: ProductNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content=_error_payload("PRODUCT_NOT_FOUND", str(exc), request.url.path))

    @app.exception_handler(DuplicateSKUError)
    async def duplicate_sku_handler(request: Request, exc: DuplicateSKUError) -> JSONResponse:
        return JSONResponse(status_code=409, content=_error_payload("DUPLICATE_SKU", str(exc), request.url.path))

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(exc.status_code, f"HTTP_{exc.status_code}")
        response = JSONResponse(status_code=exc.status_code, content=_error_payload(code, str(exc.detail), request.url.path))
        if exc.headers:
            response.headers.update(exc.headers)
        return response

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error on %s", request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content=_error_payload("INTERNAL_SERVER_ERROR", "Terjadi kesalahan internal pada server.", request.url.path))

    app.include_router(products_router, prefix="/api/v1")
    return app

app = create_app()
