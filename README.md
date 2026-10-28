# Sistem Manajemen Produk Toko — FastAPI Pekan 07

Backend REST API untuk mengelola produk toko, dibangun dengan FastAPI dan Pydantic V2. Struktur serta fitur mengacu pada materi HTML *Pekan 07: Perancangan dan Implementasi REST API Berbasis FastAPI*: RESTful naming, skema Create/Update/Response, router modular, dependency injection, API key, RBAC, centralized error handling, Swagger/OpenAPI, dan automated testing.

## Fitur

- CRUD produk: SKU, nama, harga, stok, kategori, deskripsi, dan waktu dibuat.
- Filter daftar produk dengan `category` dan pencarian `q`.
- Validasi Pydantic V2: SKU dinormalisasi menjadi huruf kapital, harga harus lebih dari nol, stok tidak boleh negatif, dan pembaruan parsial menggunakan `PATCH`.
- SKU unik; duplikasi menghasilkan HTTP `409 Conflict`.
- Auth melalui header `X-API-Key`, bukan query parameter URL.
- RBAC: STAFF dan ADMIN dapat menambah/memperbarui produk; hanya ADMIN yang dapat menghapus.
- Format error terpusat untuk validasi, autentikasi, otorisasi, produk tidak ditemukan, SKU duplikat, dan kegagalan server.
- Unit test service, API tests dengan FastAPI `TestClient`, serta GitHub Actions CI.

> **Batasan demo:** repository masih in-memory. Data akan hilang saat proses server dimulai ulang. Ini disengaja supaya fokus praktikum tetap pada desain API, SOLID, Git, dan testing, bukan konfigurasi database.

## Struktur folder

```text
app/
├── api/v1/products.py          # HTTP routes / controller
├── core/config.py              # Konfigurasi aplikasi dan API key
├── domain/product.py           # Entitas domain Product
├── domain/principal.py         # Identitas dan role pengguna
├── repositories/interfaces.py  # Kontrak repository (DIP)
├── repositories/in_memory.py   # Implementasi penyimpanan
├── schemas/product.py          # Pydantic DTO Create/Update/Read
├── services/product_service.py # Aturan bisnis
├── services/exceptions.py     # Exception domain
├── dependencies.py             # Depends, auth dan RBAC
└── main.py                     # Application factory, handlers, router

tests/
├── conftest.py
├── test_products_api.py        # Uji endpoint/integrasi
└── unit/test_product_service.py # Unit test service
```

## Cara menjalankan (Windows PowerShell)

1. Ekstrak ZIP dan buka terminal di folder project.
2. Buat virtual environment dan instal dependensi:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3. Jalankan server:

```powershell
uvicorn app.main:app --reload
```

4. Buka dokumentasi interaktif: <http://127.0.0.1:8000/docs>. Alternatif dokumentasi: <http://127.0.0.1:8000/redoc>.

### Menjalankan test

```powershell
pytest -v
```

## Autentikasi demo

Masukkan header `X-API-Key` saat menguji endpoint yang mengubah data.

| Role | API Key demo | Hak akses |
|---|---|---|
| STAFF | `staff-demo-key` | Membuat dan memperbarui produk |
| ADMIN | `admin-demo-key` | Membuat, memperbarui, dan menghapus produk |
| Publik | Tidak menggunakan key | Membaca dan mencari produk |

Contoh membuat produk:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/v1/products" `
  -H "Content-Type: application/json" `
  -H "X-API-Key: staff-demo-key" `
  -d '{"sku":"KB-001","name":"Keyboard Mechanical","price":450000,"stock":10,"category":"Aksesoris","description":"Keyboard untuk komputer"}'
```

Ganti API key demo melalui environment variable sebelum menjalankan server. Contoh `.env.example` hanya dokumentasi; aplikasi membaca environment variables sistem, sehingga file `.env` tidak otomatis dimuat.

PowerShell:

```powershell
$env:PRODUCT_ADMIN_API_KEY = "ganti-dengan-key-admin-yang-kuat"
$env:PRODUCT_STAFF_API_KEY = "ganti-dengan-key-staff-yang-kuat"
uvicorn app.main:app --reload
```

Jangan menggunakan key demo di lingkungan produksi.

## REST endpoints

Base path: `/api/v1`

| Method | Endpoint | Hak akses | Hasil normal |
|---|---|---|---|
| `GET` | `/products` | Publik | `200 OK` |
| `GET` | `/products/{product_id}` | Publik | `200 OK` |
| `POST` | `/products` | STAFF/ADMIN | `201 Created` |
| `PATCH` | `/products/{product_id}` | STAFF/ADMIN | `200 OK` |
| `DELETE` | `/products/{product_id}` | ADMIN | `204 No Content` |

Contoh query:

- `GET /api/v1/products?category=Aksesoris`
- `GET /api/v1/products?q=keyboard`

Contoh payload `POST`:

```json
{
  "sku": "KB-001",
  "name": "Keyboard Mechanical",
  "price": 450000,
  "stock": 10,
  "category": "Aksesoris",
  "description": "Keyboard untuk komputer"
}
```

Contoh pembaruan parsial `PATCH`:

```json
{
  "stock": 7
}
```

## Format error

Respons error mengikuti bentuk seragam, misalnya validasi `422`:

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Data request tidak valid.",
  "path": "/api/v1/products",
  "details": [
    {"field": "body -> price", "message": "Input should be greater than 0"}
  ]
}
```

Status utama: `401` API key tidak ada/tidak valid, `403` role tidak diizinkan, `404` produk tidak ditemukan, `409` SKU duplikat, `422` validasi gagal, dan `500` kesalahan internal tanpa membocorkan traceback.

## Penerapan SOLID

- **S — Single Responsibility Principle:** router menangani HTTP; `ProductService` mengatur bisnis; repository menyimpan/mengambil data; schema memvalidasi kontrak data.
- **O — Open/Closed Principle:** implementasi penyimpanan dapat diganti dengan repository lain tanpa mengubah aturan bisnis.
- **L — Liskov Substitution Principle:** setiap implementasi repository yang memenuhi `ProductRepository` dapat dipasangkan ke `ProductService`.
- **I — Interface Segregation Principle:** kontrak repository memuat operasi produk yang dibutuhkan, bukan satu interface besar untuk banyak domain.
- **D — Dependency Inversion Principle:** `ProductService` bergantung pada `ProductRepository` (Protocol), bukan langsung pada `InMemoryProductRepository`; object disuntikkan lewat dependency provider.

## Git workflow

Project ini disiapkan sebagai repository Git. Periksa status/riwayat:

```bash
git status
git log --oneline
```

Pola kerja perubahan fitur:

```bash
git switch -c feat/nama-fitur
# edit kode dan/atau test
pytest -v
git add .
git commit -m "feat: jelaskan perubahan"
```

Untuk membuat remote GitHub, buat repository kosong di GitHub, lalu jalankan perintah sesuai URL repository milik sendiri:

```bash
git remote add origin https://github.com/USERNAME/NAMA-REPOSITORY.git
git push -u origin main
```

Jangan memasukkan `.env`, token, atau API key rahasia ke Git. `.gitignore` sudah mengabaikan file tersebut. Workflow `.github/workflows/tests.yml` menjalankan `pytest -v` setiap push dan pull request.
