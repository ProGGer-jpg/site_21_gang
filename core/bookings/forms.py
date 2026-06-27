from django import forms
from .models import Booking

class QuickBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['client_name', 'client_phone', 'disc', 'room', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя клиента'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}),
            'disc': forms.Select(attrs={'class': 'form-control'}),
            'room': forms.Select(attrs={'class': 'form-control'}),
        }