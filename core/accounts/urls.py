from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_employee, name='register_employee'),
    path('profile/', views.profile_view, name='profile'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]