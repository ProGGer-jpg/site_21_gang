from django.contrib import admin
from .models import Tournament, TournamentParticipant  # Добавил TournamentParticipant


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['title', 'game', 'date', 'time', 'location', 'max_participants', 'created_by']
    list_filter = ['date', 'game']
    search_fields = ['title', 'game__title', 'location']
    date_hierarchy = 'date'


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'tournament', 'registered_at']
    list_filter = ['tournament', 'registered_at']
    search_fields = ['user__username', 'user__first_name', 'tournament__title']