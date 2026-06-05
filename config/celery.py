import os
from celery import Celery

# Atur default settings Django untuk program celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('simple_lms')

# Mengambil konfigurasi dari settings.py dengan prefix 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Otomatis mencari berkas bernama tasks.py di setiap aplikasi/apps yang terdaftar
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')