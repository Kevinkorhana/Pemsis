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
Project ini merupakan pengembangan lanjutan dari *Simple Learning Management System (LMS)* menggunakan arsitektur modern *multi-container orchestration*[cite: 1]. Backend dibangun menggunakan framework **Django dengan Django Ninja REST API**, serta didukung oleh **PostgreSQL** sebagai database utama, **Redis** untuk manajemen cache, **MongoDB** untuk pencatatan log aktivitas, serta **Celery + RabbitMQ** untuk menangani antrean tugas asinkronus dan terjadwal (*background & scheduled tasks*)[cite: 1].

## 2. Fitur Dasar yang Sudah Berjalan
* **Authentication**: Autentikasi aman menggunakan JWT Tokens (`AuthBearer`)[cite: 1].
* **Role-Based Access Control (RBAC)**: Pembatasan hak akses berbasis peran untuk Admin, Instructor, dan Student[cite: 1].
* **Core LMS Endpoints**: Manajemen data Course, Lesson, Enrollment, dan Progress tracking[cite: 1].
* **Auto-Generated Documentation**: Swagger/OpenAPI interaktif diakses melalui `/api/docs`[cite: 1].

## 3. Fitur Tambahan yang Dipilih (Paket 4 - Performance & API Quality)
Sesuai dengan ketentuan, berikut adalah daftar fitur lanjutan yang berhasil diimplementasikan pada project ini[cite: 1]:

| No | Fitur Tambahan                           | Kategori              | Poin | Status                   |
|----|------------------------------------------|-----------------------|------|--------------------------|
| 1  | Redis caching untuk course               | D. Redis & Caching    | 12   | Selesai[cite: 1]         |
| 2  | Cache invalidation strategy              | D. Redis & Caching    | 12   | Selesai[cite: 1]         |
| 3  | Filter, search, sort, pagination lengkap | I. API Quality        | 12   | Selesai[cite: 1]         |
| 4  | Email notification async via Celery      | F. Celery & Async     | 12   | Selesai[cite: 1]         |
| 5  | Flower monitoring                        | F. Celery & Async     | 8    | Selesai[cite: 1]         |
| **Total Poin**                                | **56 Poin**           | **Maksimal (50 Poin)**[cite: 1] |

## 4. Penjelasan Implementasi Fitur Tambahan

### A. Filter, Search, Sort, dan Pagination pada List Course
Endpoint `GET /api/courses/` dimodifikasi menggunakan `CourseFilterSchema`[cite: 1]. Pengguna dapat mencari course berdasarkan kata kunci (`search`), menyaring berdasarkan tingkat kesulitan (`level`), dan mengurutkannya (`sort_by`) secara dinamis dengan query SQL yang dioptimalkan menggunakan parameter `limit` dan `offset`[cite: 1].

### B. Redis Caching & Invalidation Strategy
* **Caching**: Detail course (`GET /api/courses/{course_id}`) dibungkus menggunakan Redis Cache (`cache.get`/`cache.set`) dengan TTL 15 menit[cite: 1]. Request berulang terhadap data yang sama tidak akan membebani database PostgreSQL, melainkan langsung ditarik secara instan dari RAM Redis (*Cache Hit*)[cite: 1].
* **Invalidation**: Guna menghindari data basi (*stale data*), fungsi helper `clear_course_cache()` akan dipicu secara otomatis untuk menghapus cache di Redis setiap kali Instructor melakukan aksi pembuatan, pembaruan (*patch*), atau penghapusan (*delete*) course[cite: 1].

### C. Asynchronous Task & Notification via Celery
Proses pengiriman email notifikasi saat mahasiswa mendaftar kursus (`POST /api/courses/enrollments`) dilempar ke background worker Celery menggunakan perintah `.delay()`[cite: 1]. Hal ini memangkas waktu respons API secara ekstrem karena server tidak perlu tertahan menunggu proses jaringan eksternal selesai[cite: 1].

### D. Flower Monitoring Integration
Dashboard monitoring Flower diintegrasikan ke dalam berkas `docker-compose.yml` pada port `5555` untuk mengamati status keberhasilan, kegagalan, dan statistik beban antrean task yang dikerjakan oleh Celery worker secara real-time[cite: 1].

## 5. Cara Menjalankan Project
1. Pastikan Docker Desktop sudah aktif di komputer Anda[cite: 1].
2. Jalankan seluruh layanan *stack orchestration* menggunakan perintah:
   ```powershell
   docker compose up -d --build
   ```[cite: 1]
3. Jalankan migrasi database (jika diperlukan):
   ```powershell
   docker compose exec web python manage.py migrate
   ```[cite: 1]

## 6. Akun Demo Pengujian
* **Admin**: `admin` / `1234`[cite: 1]
* **Instructor**: `instructor` / `password123`[cite: 1]
* **Student**: `student` / `password123`[cite: 1]

## 7. Endpoint Penting untuk Diuji
* **Dokumentasi Swagger**: `http://localhost:8000/api/docs`[cite: 1]
* **List Course (Filter & Search)**: `GET /api/courses/?search=python&level=beginner&sort_by=title`[cite: 1]
* **Detail Course (Redis Cache)**: `GET /api/courses/{id}`[cite: 1]
* **Trigger Enroll (Celery Email)**: `POST /api/courses/enrollments`[cite: 1]
* **Flower Dashboard**: `http://localhost:5555`[cite: 1]

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
Melalui pengerjaan Final Project ini, pengembang berhasil memahami secara mendalam arsitektur backend berskala production[cite: 1]. Integrasi Redis terbukti memangkas latensi pembacaan data, sementara arsitektur asynchronous menggunakan Celery dan RabbitMQ menjaga aplikasi tetap responsif[cite: 1]. Ditambah dengan isolasi lingkungan Docker Compose, sistem menjadi sangat mudah di-deploy dan dikelola[cite: 1].