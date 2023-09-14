from django.urls import path, include
from . import views

app_name = 'deposit'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # path('index', views.index, name='index'),
    path('screen/', views.screen, name='screen'),
]

