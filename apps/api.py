from ninja import NinjaAPI
from authentication.api import router as auth_router
from courses.api import router as course_router

api = NinjaAPI(title="Simple LMS API")

api.add_router("/auth/", auth_router)

api.add_router("/courses/", course_router)