from django.urls import path
from . import views

urlpatterns = [
    path('', views.quick_booking, name='quick_booking'),
]