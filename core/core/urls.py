from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bookings.urls')), # Главная страница - это бронирование
    path('accounts/', include('accounts.urls')),
]