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

