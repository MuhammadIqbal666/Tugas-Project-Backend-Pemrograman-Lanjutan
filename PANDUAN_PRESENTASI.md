# Panduan Singkat Presentasi

## Tujuan
Membangun REST API backend agar data produk toko dapat dibuat, dibaca, diperbarui, dicari, dan dihapus lewat kontrak HTTP/JSON.

## Alur arsitektur
1. Client mengirim request ke router `/api/v1/products`.
2. FastAPI/Pydantic memvalidasi request body dan parameter.
3. `Depends()` menyiapkan service/repository, dan memeriksa API key untuk endpoint terproteksi.
4. `ProductService` menjalankan aturan bisnis, seperti menolak SKU duplikat.
5. `ProductRepository` menjalankan penyimpanan; implementasi saat ini adalah in-memory.
6. FastAPI mengubah entitas menjadi DTO `ProductRead`; exception diubah menjadi JSON error yang konsisten.

## Contoh demo
1. Buka `/docs`.
2. Jalankan `GET /api/v1/products` tanpa autentikasi.
3. Gunakan `POST /api/v1/products` dengan header `X-API-Key: staff-demo-key`.
4. Ulangi SKU yang sama untuk melihat `409 Conflict`.
5. Kirim harga `0` atau stok negatif untuk melihat `422 Validation Error`.
6. Coba `DELETE` dengan `staff-demo-key` (harus `403`), lalu `admin-demo-key` (berhasil `204`).
7. Jalankan `pytest -v` untuk membuktikan perilaku API dan service diuji otomatis.

## Pesan utama
Modularitas memisahkan tanggung jawab; SOLID membuat aturan bisnis tidak terikat pada implementasi database; Git menyimpan riwayat perubahan; automated test mengurangi risiko regresi.
