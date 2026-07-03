from functools import wraps
from ninja.errors import HttpError

def is_instructor(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        # 1. Pastikan user sudah terautentikasi
        if not request.auth:
            raise HttpError(401, "Unauthorized")
        
        # 2. Proteksi check: Pastikan user memiliki objek profile di database
        if not hasattr(request.auth, 'profile') or request.auth.profile is None:
            raise HttpError(403, "Forbidden: Profil pengguna belum dikonfigurasi.")
            
        # 3. Cek apakah role pengguna adalah instructor atau admin
        if request.auth.profile.role not in ['instructor', 'admin']:
            raise HttpError(403, "Forbidden: Anda bukan seorang Instructor.")
            
        return func(request, *args, **kwargs)
    return wrapper