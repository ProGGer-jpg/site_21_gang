from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'disc', 'room', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'room', 'disc__game__platform')
    search_fields = ('client_name', 'client_phone', 'disc__barcode')
    date_hierarchy = 'start_time'

    fieldsets = (
        ('Клиент', {'fields': ('client_name', 'client_phone')}),
        ('Что и где', {'fields': ('disc', 'room')}),
        ('Время', {'fields': ('start_time', 'end_time', 'status')}),
        ('Дополнительно', {'fields': ('notes',)}),
    )