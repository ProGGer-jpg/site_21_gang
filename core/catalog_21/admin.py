from django.contrib import admin
from .models import Platform, Game, Disc, Room


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'genre')
    list_filter = ('platform', 'genre')
    search_fields = ('title',)


@admin.register(Disc)
class DiscAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'game', 'status', 'condition', 'purchase_date')
    list_filter = ('status', 'game__platform')
    search_fields = ('barcode', 'game__title')

    # При создании диска сразу предлагаем выбрать игру
    autocomplete_fields = ('game',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'is_active')
    list_filter = ('platform', 'is_active')
