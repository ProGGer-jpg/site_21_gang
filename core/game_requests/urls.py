from django.urls import path
from . import views

app_name = 'game_requests'

urlpatterns = [
    path('submit/', views.submit_request, name='submit_request'),
    path('', views.request_list, name='request_list'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
]