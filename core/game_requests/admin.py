from django.contrib import admin
from .models import GameRequest


@admin.register(GameRequest)
class GameRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'requester', 'status', 'created_at')
    list_filter = ('status', 'platform', 'created_at')
    search_fields = ('title', 'reason', 'requester__username')
    readonly_fields = ('created_at', 'updated_at', 'requester')
    list_editable = ('status',)