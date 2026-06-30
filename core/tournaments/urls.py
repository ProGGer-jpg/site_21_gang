from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.tournament_list, name='tournament_list'),
    path('create/', views.tournament_create, name='tournament_create'),
    path('<int:pk>/edit/', views.tournament_edit, name='tournament_edit'),
    path('<int:pk>/delete/', views.tournament_delete, name='tournament_delete'),
    path('<int:pk>/join/', views.tournament_join, name='tournament_join'),
    path('<int:pk>/leave/', views.tournament_leave, name='tournament_leave'),
]