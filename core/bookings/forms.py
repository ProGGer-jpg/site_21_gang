from django import forms
from django.core.exceptions import ValidationError
from datetime import timedelta
from .models import Booking


class QuickBookingForm(forms.ModelForm):
    MAX_HOURS = Booking.MAX_HOURS # Максимальное время бронирования в часах

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

    def __init__(self, *args, **kwargs):
        # Получаем текущего пользователя
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ВАЖНО: Привязываем сотрудника к экземпляру модели ДО валидации
        if self.user:
            self.instance.employee = self.user

        # Автозаполнение имени клиента (только для новых броней)
        if self.user and not self.instance.pk:
            self.fields['client_name'].initial = self.user.get_full_name() or self.user.username

        if self.user and self.user.is_authenticated:
            self.instance.employee = self.user
            if not self.instance.pk:
                self.fields['client_name'].initial = self.user.get_full_name() or self.user.username

    # def clean(self):
    #     cleaned_data = super().clean()
    #     start_time = cleaned_data.get('start_time')
    #     end_time = cleaned_data.get('end_time')
    #
    #     if start_time and end_time:
    #         duration = end_time - start_time
    #
    #         if duration > timedelta(hours=self.MAX_HOURS):
    #             raise ValidationError(
    #                 f'⏰ Бронирование не может быть дольше {self.MAX_HOURS} часов! '
    #                 f'Вы указали {duration.seconds // 3600} ч. {duration.seconds % 3600 // 60} мин.'
    #             )
    #
    #         if duration <= timedelta(0):
    #             raise ValidationError('⏰ Время окончания должно быть позже времени начала!')
    #
    #         if duration < timedelta(minutes=30):
    #             raise ValidationError('⏰ Минимальное время бронирования — 30 минут!')
    #
    #     return cleaned_data