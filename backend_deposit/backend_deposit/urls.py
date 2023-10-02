from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
# urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', include('api.urls')),
urlpatterns = [
    path('', include('deposit.urls', namespace='deposit')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
]