# Progress 1 : Simple LMS - Docker & Django Foundation

## Cara Menjalankan Project
1. Run Environment  File :
'cp .env.example .env'
2. Jalankan Docker :
'docker compose up --build'
3. Migrasi Database :
'docker compose exec web python manage.py migrate'
4. Akses Aplikasi :
http://localhost:8000/
http://localhost:8000/admin/

## Environment variables setup
| Variable    | Keterangan                       |
|-------------|----------------------------------|
| DEBUG       | Mode development (1 = aktif)     |
| SECRET_KEY  | Secret key untuk keamanan Django |
| DB_NAME     | Nama database PostgreSQL         |
| DB_USER     | Username database                |
| DB_PASSWORD | Password database                |
| DB_HOST     | Host database (db dari Docker)   |
| DB_PORT     | Port database (5432)             |

## Screenshot

### Django Welcome Page
![Django](screenshots/Django.png)
![AdminDjango](screenshots/AdminDjango.png)

---

# Progress 2: Database Design & ORM

## Data Models
- User + Profile (Role)
- Category (hierarchy)
- Course
- Lesson
- Enrollment
- Progress

## Query Optimization

### Tanpa Optimization (N+1 Problem)
Jumlah query: 4

### Dengan Optimization
Jumlah query: 1

## Fixtures
Data awal diexport menggunakan:
docker compose exec web python manage.py dumpdata > fixtures.json

```bash
screenshots/
├── AdminDjango.png
├── course.png
├── query.png
├── profiles.png