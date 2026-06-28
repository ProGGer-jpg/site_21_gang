from django import forms
from .models import GameRequest


class GameRequestForm(forms.ModelForm):
    class Meta:
        model = GameRequest
        fields = ['title', 'platform', 'reason']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: GTA VI',
            }),
            'platform': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Почему эту игру стоит добавить?',
            }),
        }


class AdminCommentForm(forms.ModelForm):
    class Meta:
        model = GameRequest
        fields = ['status', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
            }),
        }