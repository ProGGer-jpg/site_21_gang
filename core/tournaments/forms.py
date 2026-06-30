from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Tournament


class TournamentForm(forms.ModelForm):
    """Форма для создания и редактирования турниров"""

    class Meta:
        model = Tournament
        fields = ['title', 'game', 'description', 'date', 'time', 'location', 'max_participants']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'game': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_date(self):
        """Проверка даты"""
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise ValidationError('Дата турнира не может быть в прошлом.')
        return date

    def clean_time(self):
        """Проверка времени"""
        time = self.cleaned_data.get('time')
        return time

    def clean(self):
        """Проверяем, что дата и время турнира не в прошлом"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            # Собираем дату и время турнира
            tournament_datetime = timezone.datetime.combine(date, time)
            # Делаем timezone-aware если USE_TZ=True
            if timezone.is_naive(tournament_datetime):
                tournament_datetime = timezone.make_aware(tournament_datetime)

            now = timezone.now()

            # Если турнир в прошлом — ошибка
            if tournament_datetime < now:
                raise ValidationError(
                    'Это время или дата не подходит. '
                    'Нельзя создать турнир в прошлом.'
                )

        return cleaned_data