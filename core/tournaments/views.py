from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Tournament, TournamentParticipant
from .forms import TournamentForm


def tournament_list(request):
    """Список всех турниров"""
    tournaments = Tournament.objects.filter(date__gte=timezone.now().date())
    past_tournaments = Tournament.objects.filter(date__lt=timezone.now().date())[:5]

    # Если пользователь авторизован, добавляем информацию об его участии
    if request.user.is_authenticated:
        for tournament in tournaments:
            tournament.is_participant = TournamentParticipant.objects.filter(
                tournament=tournament,
                user=request.user
            ).exists()

    return render(request, 'tournaments/tournament_list.html', {
        'tournaments': tournaments,
        'past_tournaments': past_tournaments,
    })


@login_required
def tournament_create(request):
    """Создание нового турнира (только для staff)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для создания турниров')
        return redirect('tournaments:tournament_list')

    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.created_by = request.user
            tournament.save()
            messages.success(request, 'Турнир успешно создан!')
            return redirect('tournaments:tournament_list')
    else:
        form = TournamentForm()

    return render(request, 'tournaments/tournament_form.html', {
        'form': form,
        'title': 'Создать турнир',
    })


@login_required
def tournament_edit(request, pk):
    """Редактирование турнира (только для staff)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования турниров')
        return redirect('tournaments:tournament_list')

    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        form = TournamentForm(request.POST, instance=tournament)
        if form.is_valid():
            form.save()
            messages.success(request, 'Турнир успешно обновлен!')
            return redirect('tournaments:tournament_list')
    else:
        form = TournamentForm(instance=tournament)

    return render(request, 'tournaments/tournament_form.html', {
        'form': form,
        'tournament': tournament,
        'title': 'Редактировать турнир',
    })


@login_required
def tournament_delete(request, pk):
    """Удаление турнира (только для staff)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для удаления турниров')
        return redirect('tournaments:tournament_list')

    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        tournament.delete()
        messages.success(request, 'Турнир успешно удален!')
        return redirect('tournaments:tournament_list')

    return render(request, 'tournaments/tournament_confirm_delete.html', {
        'tournament': tournament,
    })


@login_required
def tournament_join(request, pk):
    """Записаться на турнир"""
    tournament = get_object_or_404(Tournament, pk=pk)

    # Проверяем, не прошел ли турнир
    if tournament.date < timezone.now().date():
        messages.error(request, 'Этот турнир уже прошел')
        return redirect('tournaments:tournament_list')

    # Проверяем, не записан ли уже пользователь
    if TournamentParticipant.objects.filter(tournament=tournament, user=request.user).exists():
        messages.warning(request, 'Вы уже записаны на этот турнир')
        return redirect('tournaments:tournament_list')

    # Проверяем, есть ли места
    if tournament.tournamentparticipant_set.count() >= tournament.max_participants:
        messages.error(request, 'К сожалению, все места уже заняты')
        return redirect('tournaments:tournament_list')

    # Записываем на турнир
    TournamentParticipant.objects.create(tournament=tournament, user=request.user)
    messages.success(request, f'Вы успешно записались на турнир "{tournament.title}"')
    return redirect('tournaments:tournament_list')


@login_required
def tournament_leave(request, pk):
    """Отменить участие в турнире"""
    tournament = get_object_or_404(Tournament, pk=pk)

    participant = TournamentParticipant.objects.filter(tournament=tournament, user=request.user).first()
    if participant:
        participant.delete()
        messages.success(request, f'Вы отменили участие в турнире "{tournament.title}"')
    else:
        messages.warning(request, 'Вы не записаны на этот турнир')

    return redirect('tournaments:tournament_list')