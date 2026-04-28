from datetime import datetime, timedelta
from jose import jwt
from ninja.security import HttpBearer
from django.contrib.auth.models import User

SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            # Panggil fungsi verify_token yang ada di bawah
            data = verify_token(token)
            # Ambil user beserta profilenya
            user = User.objects.select_related('profile').get(id=data["user_id"])
            return user
        except Exception:
            return None

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=60)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(days=7)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def refresh_access_token(refresh_token: str):
    try:
        data = verify_token(refresh_token)
        # Buat access token baru dengan user_id yang sama
        new_access = create_access_token({"user_id": data["user_id"]})
        return new_access
    except Exception:
        return None