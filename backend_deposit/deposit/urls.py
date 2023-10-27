from django.conf.urls.static import static
from django.urls import path, include

from backend_deposit import settings
from . import views
from .views import ShowDeposit, deposits_list, deposits_list_pending, deposit_edit

app_name = 'deposit'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    # path('deposit_confirm/<str:phone>/<int:pay>/', views.deposit_confirm, name='deposit_confirm'),
    # path('deposit_confirm/', views.deposit_confirm, name='confirm'),
    path('deposit_created/', views.deposit_created, name='created'),
    path('deposit_status/<str:uid>/', views.deposit_status, name='status'),
    # path('index', views.index, name='index'),
    path('screen/', views.screen, name='screen'),
    # path('deposits/', DepositList.as_view(), name='deposits'),
    path('deposits/', deposits_list, name='deposits'),
    path('deposits_pending/', deposits_list_pending, name='deposits_pending'),
    # path(r'^page(?P<page>\d+)/$', DepositList.as_view(), name='deposits'),

    path('deposits/<int:pk>/', deposit_edit, name='deposit_edit'),

path('sms/', views.sms, name='sms'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
