from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Tournament


class TournamentForm(forms.ModelForm):
    """Форма для создания и редактирования турниров"""
    class Meta:
        model = Tournament
        fields = ['title', 'game', 'description', 'date', 'time', 'location', 'max_participants']  # Убрал rating_reward
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'game': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """Проверяем, что дата и время турнира не в прошлом"""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            tournament_datetime = timezone.datetime.combine(date, time)
            if timezone.is_naive(tournament_datetime):
                tournament_datetime = timezone.make_aware(tournament_datetime)

            now = timezone.now()

            if date < timezone.now().date():
                self.add_error('date', 'Эта дата не подходит')
            elif date == timezone.now().date() and tournament_datetime < now:
                self.add_error('time', 'Это время не подходит')

        return cleaned_data