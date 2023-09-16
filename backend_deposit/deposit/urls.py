from django.urls import path, include
from . import views

app_name = 'deposit'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # path('deposit_confirm/<str:phone>/<int:pay>/', views.deposit_confirm, name='deposit_confirm'),
    path('deposit_confirm/', views.deposit_confirm, name='deposit_confirm'),
    path('deposit_created/', views.deposit_created, name='deposit_created'),
    # path('index', views.index, name='index'),
    path('screen/', views.screen, name='screen'),
]

