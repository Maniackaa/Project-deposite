from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import (
    ScreenViewSet
)

app_name = "api"

v1_router = DefaultRouter()
v1_router.register("screen", ScreenViewSet, basename="screen")


urlpatterns = [
    path("", include(v1_router.urls)),
    path("api-token-auth/", views.obtain_auth_token),
]
