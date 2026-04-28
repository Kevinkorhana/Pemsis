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
        # Tambahkan role ke dalam token agar bisa dicek oleh decorator RBAC nanti
        access = create_access_token({"user_id": user.id, "role": user.profile.role})
        refresh = create_refresh_token({"user_id": user.id})
        return {"access": access, "refresh": refresh}
    
    raise HttpError(401, "Invalid credentials") # Gunakan raise untuk HttpError

@router.get("/me", auth=AuthBearer())
def me(request):
    return {
        "username": request.auth.username,
        "email": request.auth.email,
        "role": request.auth.profile.role
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