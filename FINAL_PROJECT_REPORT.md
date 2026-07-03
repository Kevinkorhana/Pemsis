# Laporan Final Project: Simple LMS Extended Backend

### Identitas Pengembang
* **Nama**: Kevin Korhan Arrizky
* **NIM**: A11.2022.14318
* **Kelas**: Pemrograman Sisi Server
* **Program Studi**: Teknik Informatika 
* **Dosen Pengajar**: Fahri Firdausillah, S.Kom, M.CS
* **URL Repository**: https://github.com/Kevinkorhana/Pemsis

---

## 1. Deskripsi Project
Project ini merupakan pengembangan lanjutan dari *Simple Learning Management System (LMS)* menggunakan arsitektur modern *multi-container orchestration*. Backend dibangun menggunakan framework **Django dengan Django Ninja REST API**, serta didukung oleh **PostgreSQL** sebagai database utama, **Redis** untuk manajemen cache, **MongoDB** untuk pencatatan log aktivitas, serta **Celery + RabbitMQ** untuk menangani antrean tugas asinkronus dan terjadwal (*background & scheduled tasks*).

## 2. Fitur Dasar yang Sudah Berjalan
* **Authentication**: Autentikasi aman menggunakan JWT Tokens (`AuthBearer`).
* **Role-Based Access Control (RBAC)**: Pembatasan hak akses berbasis peran untuk Admin, Instructor, dan Student.
* **Core LMS Endpoints**: Manajemen data Course, Lesson, Enrollment, dan Progress tracking.
* **Auto-Generated Documentation**: Swagger/OpenAPI interaktif diakses melalui `/api/docs`.
* **Multi-Container Environment**: Menggunakan Docker dan Docker Compose untuk mengisolasi lingkungan pengembangan sistem.
* **Relational Database System**: Django project yang terintegrasi secara penuh dengan database PostgreSQL untuk persistensi data utama.
* **LMS Core Models Data Structure**: Implementasi lengkap model-model utama yang saling berelasi, yaitu: `User`, `Category`, `Course`, `Lesson`, `Enrollment`, dan `Progress`.
* **Modern REST API Architecture**: Pembangunan seluruh endpoint API menggunakan framework Django Ninja untuk performa eksekusi yang cepat dan validasi skema otomatis.
* **Secure JWT Authentication**: Sistem pengamanan data dan session pengguna menggunakan mekanisme JWT (JSON Web Token) via dekorator kustom `AuthBearer`.
* **LMS Fundamental Endpoints**: Ketersediaan API endpoint dasar yang matang untuk manajemen siklus hidup `course`, proses `enrollment`, serta pelacakan `progress` materi.

## 3. Fitur Tambahan yang Dipilih (Paket 4 - Performance & API Quality)

| No | Fitur Tambahan                           | Kategori              | Poin | Status                   |
|----|------------------------------------------|-----------------------|------|--------------------------|
| 1  | Redis caching untuk course               | D. Redis & Caching    | 12   | Selesai                  |
| 2  | Cache invalidation strategy              | D. Redis & Caching    | 12   | Selesai                  |
| 3  | Filter, search, sort, pagination lengkap | I. API Quality        | 12   | Selesai                  |
| 4  | Email notification async via Celery      | F. Celery & Async     | 12   | Selesai                  |
| 5  | Flower monitoring                        | F. Celery & Async     | 8    | Selesai                  |
| **Total Poin**                                | **56 Poin**           | **Maksimal (50 Poin)**          |

## 4. Penjelasan Implementasi Fitur Tambahan

### A. Filter, Search, Sort, dan Pagination pada List Course
Endpoint `GET /api/courses/` dimodifikasi menggunakan `CourseFilterSchema`. Pengguna dapat mencari course berdasarkan kata kunci (`search`), menyaring berdasarkan tingkat kesulitan (`level`), dan mengurutkannya (`sort_by`) secara dinamis dengan query SQL yang dioptimalkan menggunakan parameter `limit` dan `offset`.

### B. Redis Caching & Invalidation Strategy
* **Caching**: Detail course (`GET /api/courses/{course_id}`) dibungkus menggunakan Redis Cache (`cache.get`/`cache.set`) dengan TTL 15 menit. Request berulang terhadap data yang sama tidak akan membebani database PostgreSQL, melainkan langsung ditarik secara instan dari RAM Redis (*Cache Hit*).
* **Invalidation**: Guna menghindari data basi (*stale data*), fungsi helper `clear_course_cache()` akan dipicu secara otomatis untuk menghapus cache di Redis setiap kali Instructor melakukan aksi pembuatan, pembaruan (*patch*), atau penghapusan (*delete*) course.

### C. Asynchronous Task & Notification via Celery
Proses pengiriman email notifikasi saat mahasiswa mendaftar kursus (`POST /api/courses/enrollments`) dilempar ke background worker Celery menggunakan perintah `.delay()`. Hal ini memangkas waktu respons API secara ekstrem karena server tidak perlu tertahan menunggu proses jaringan eksternal selesai.

### D. Flower Monitoring Integration
Dashboard monitoring Flower diintegrasikan ke dalam berkas `docker-compose.yml` pada port `5555` untuk mengamati status keberhasilan, kegagalan, dan statistik beban antrean task yang dikerjakan oleh Celery worker secara real-time.

## 5. Cara Menjalankan Project
1. Pastikan Docker Desktop sudah aktif di komputer Anda.
2. Jalankan seluruh layanan *stack orchestration* menggunakan perintah:
   ```powershell
   docker compose up -d --build
3. Jalankan migrasi database (jika diperlukan):
   ```powershell
   docker compose exec web python manage.py migrate

## 6. Akun Demo Pengujian
* **Admin**: `admin` / `1234`
* **Instructor**: `instructor` / `password123`
* **Student**: `student` / `password123`

## 7. Endpoint Penting untuk Diuji
* **Dokumentasi Swagger**: `http://localhost:8000/api/docs`
* **List Course (Filter & Search)**: `GET /api/courses/?search=python&level=beginner&sort_by=title`
* **Detail Course (Redis Cache)**: `GET /api/courses/{id}`
* **Trigger Enroll (Celery Email)**: `POST /api/courses/enrollments`
* **Flower Dashboard**: `http://localhost:5555`

## 8. Screenshot / Bukti Pengujian

### A. Dokumentasi API (Swagger UI Overview)
![Swagger UI](swagger_overview.png)

### B. Pengujian List Course (Search & Pagination)
![List Course](screenshot_list_course.png)

### C. Pengujian Detail Course (Redis Caching)
![Detail Course](screenshot_detail_course.png)

### D. Pengujian Trigger Enroll & Celery Background Task
![Enroll Task](screenshot_enroll.png)

### E. Dashboard Monitoring Flower Interface
![Flower Dashboard](flower_dashboard.png)

## 9. Kendala dan Solusi
* **Kendala**: Terjadi konflik port (*port conflict*) pada port default `8080` dan `6379` karena adanya sisa kontainer dari latihan pengujian Redis Caching dan WordPress terpisah sebelumnya.
* **Solusi**: Menghentikan kontainer latihan lama yang sudah tidak digunakan menggunakan `docker stop` atau mengalihkan port pemetaan eksternal agar seluruh ekosistem kontainer utama *Simple LMS* dapat mengunci jalurnya dengan aman tanpa bentrokan.

## 10. Kesimpulan
Melalui pengerjaan Final Project ini, pengembang berhasil memahami secara mendalam arsitektur backend berskala production. Integrasi Redis terbukti memangkas latensi pembacaan data, sementara arsitektur asynchronous menggunakan Celery dan RabbitMQ menjaga aplikasi tetap responsif. Ditambah dengan isolasi lingkungan Docker Compose, sistem menjadi sangat mudah di-deploy dan dikelola.
