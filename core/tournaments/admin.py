from django.contrib import admin
from .models import Tournament, TournamentParticipant, TournamentResult, PlayerRating


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ['title', 'game', 'date', 'time', 'location', 'max_participants', 'status', 'created_by']
    list_filter = ['date', 'game', 'status']
    search_fields = ['title', 'game__title', 'location']
    date_hierarchy = 'date'


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'tournament', 'registered_at']
    list_filter = ['tournament', 'registered_at']
    search_fields = ['user__username', 'user__first_name', 'tournament__title']


@admin.register(TournamentResult)
class TournamentResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'tournament', 'place']
    list_filter = ['tournament', 'place']
    search_fields = ['user__username', 'tournament__title']


@admin.register(PlayerRating)
class PlayerRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'updated_at']
    search_fields = ['user__username', 'user__first_name']