from ninja import Router, Schema
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# Gunakan titik (.) untuk file di folder yang sama
from .models import Profile
from .jwt import create_access_token, create_refresh_token, AuthBearer
router = Router(tags=["Authentication"])

class RegisterSchema(Schema):
    username: str
    password: str
    email: str
    role: str = "student"

class LoginSchema(Schema):
    username: str
    password: str

class TokenRefreshSchema(Schema):
    refresh: str

class ProfileUpdateSchema(Schema):
    email: str = None

@router.post("/register")
def register(request, data: RegisterSchema):
    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")
        
    user = User.objects.create_user(
        username=data.username, 
        password=data.password, 
        email=data.email
    )
    # Profile dibuat secara manual karena OneToOneField
    Profile.objects.create(user=user, role=data.role)
    return {"message": "User created successfully"}

@router.post("/login")
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user:
        try:
            # Skenario Aman 1: Jika model Profile menggunakan field custom (misal id-nya sama dengan user_id)
            profile, created = Profile.objects.get_or_create(
                id=user.id,
                defaults={'role': 'admin' if user.is_superuser else 'student'}
            )
            role = profile.role
        except Exception:
            # Skenario Aman 2 (FALLBACK): Jika tabel Profile benar-benar kosong/kaku,
            # bypass langsung rolenya tanpa memaksa query ke database agar tidak crash 500!
            role = 'admin' if user.is_superuser else 'student'
            
        access = create_access_token({"user_id": user.id, "role": role})
        refresh = create_refresh_token({"user_id": user.id})
        return {"access": access, "refresh": refresh}
    
    raise HttpError(401, "Invalid credentials")

@router.get("/me", auth=AuthBearer())
def me(request):
    try:
        profile = Profile.objects.filter(id=request.auth.id).first()
        role = profile.role if profile else ('admin' if request.auth.is_superuser else 'student')
    except Exception:
        role = 'admin' if request.auth.is_superuser else 'student'
        
    return {
        "username": request.auth.username,
        "email": request.auth.email,
        "role": role
    }
    
@router.post("/refresh")
def refresh_token(request, data: TokenRefreshSchema):
    from .jwt import refresh_access_token
    new_token = refresh_access_token(data.refresh)
    if not new_token:
        raise HttpError(401, "Invalid or expired refresh token")
    return {"access": new_token}

# Endpoint Update Profile
@router.put("/me", auth=AuthBearer())
def update_me(request, data: ProfileUpdateSchema):
    user = request.auth
    if data.email:
        user.email = data.email
        user.save()
    # Update field lain di user.profile jika diperlukan
    return {"message": "Profile updated"}