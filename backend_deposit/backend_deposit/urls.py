from django.contrib import admin
from django.urls import path, include

# urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('api/', include('api.urls')),
urlpatterns = [
    path('', include('deposit.urls', namespace='deposit')),
    path('admin/', admin.site.urls),
]
