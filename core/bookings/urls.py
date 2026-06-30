from django.urls import path
from . import views

urlpatterns = [
    path('', views.quick_booking, name='quick_booking'),
    path('games/', views.games_catalog, name='games_catalog'),
    path('rooms/', views.rooms_catalog, name='rooms_catalog'),
]