from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils import timezone
from .models import Tournament, TournamentParticipant, TournamentResult, PlayerRating
from .forms import TournamentForm

User = get_user_model()


def tournament_list(request):
    """Список всех турниров"""
    # Автоматически завершаем турниры, которые прошли более 10 часов назад
    ten_hours_ago = timezone.now() - timezone.timedelta(hours=10)
    old_tournaments = Tournament.objects.filter(
        status=Tournament.Status.UPCOMING,
        date__lt=timezone.now().date()
    )
    for tournament in old_tournaments:
        tournament_datetime = timezone.datetime.combine(tournament.date, tournament.time)
        if timezone.is_naive(tournament_datetime):
            tournament_datetime = timezone.make_aware(tournament_datetime)
        if tournament_datetime < ten_hours_ago:
            tournament.status = Tournament.Status.FINISHED
            tournament.finished_at = timezone.now()
            tournament.save()

    # Автоматически удаляем завершённые турниры старше 5 часов
    five_hours_ago = timezone.now() - timezone.timedelta(hours=5)
    Tournament.objects.filter(
        status=Tournament.Status.FINISHED,
        finished_at__lt=five_hours_ago
    ).delete()

    upcoming = Tournament.objects.filter(status=Tournament.Status.UPCOMING)
    finished = Tournament.objects.filter(status=Tournament.Status.FINISHED)

    # Если пользователь авторизован, добавляем информацию об его участии
    if request.user.is_authenticated:
        for tournament in upcoming:
            tournament.is_participant = TournamentParticipant.objects.filter(
                tournament=tournament,
                user=request.user
            ).exists()

    return render(request, 'tournaments/tournament_list.html', {
        'upcoming_tournaments': upcoming,
        'finished_tournaments': finished,
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

    try:
        tournament = Tournament.objects.get(pk=pk)
    except Tournament.DoesNotExist:
        messages.error(request, 'Турнир не найден или уже удалён')
        return redirect('tournaments:tournament_list')

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

    if tournament.date < timezone.now().date():
        messages.error(request, 'Этот турнир уже прошел')
        return redirect('tournaments:tournament_list')

    if TournamentParticipant.objects.filter(tournament=tournament, user=request.user).exists():
        messages.warning(request, 'Вы уже записаны на этот турнир')
        return redirect('tournaments:tournament_list')

    if tournament.tournamentparticipant_set.count() >= tournament.max_participants:
        messages.error(request, 'К сожалению, все места уже заняты')
        return redirect('tournaments:tournament_list')

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


@login_required
def tournament_finish(request, pk):
    """Завершить турнир и начислить рейтинг"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для завершения турниров')
        return redirect('tournaments:tournament_list')

    tournament = get_object_or_404(Tournament, pk=pk)

    if request.method == 'POST':
        participants_with_places = []

        for participant in tournament.tournamentparticipant_set.all():
            place_key = f'place_{participant.user.pk}'
            rating_key = f'rating_{participant.user.pk}'

            place = request.POST.get(place_key)
            rating = request.POST.get(rating_key)

            if place and place.strip():
                try:
                    place = int(place)
                    rating_points = int(rating) if rating and rating.strip() else 0

                    participants_with_places.append({
                        'user': participant.user,
                        'place': place,
                        'rating': rating_points
                    })
                except ValueError:
                    pass

        if not participants_with_places:
            messages.error(request, 'Выберите хотя бы одного победителя (укажите место)')
            return redirect('tournaments:tournament_edit', pk=pk)

        places = [p['place'] for p in participants_with_places]
        if len(places) != len(set(places)):
            messages.error(request, 'Одно и то же место нельзя присвоить нескольким участникам')
            return redirect('tournaments:tournament_edit', pk=pk)

        tournament.status = Tournament.Status.FINISHED
        tournament.finished_at = timezone.now()
        tournament.save()

        participants_with_places.sort(key=lambda x: x['place'])

        for participant_data in participants_with_places:
            user = participant_data['user']
            place = participant_data['place']
            rating_points = participant_data['rating']

            TournamentResult.objects.create(
                tournament=tournament,
                user=user,
                place=place
            )

            if rating_points > 0:
                player_rating, created = PlayerRating.objects.get_or_create(
                    user=user,
                    defaults={'rating': 0}
                )
                player_rating.rating += rating_points
                player_rating.save()

        messages.success(request, f'Турнир "{tournament.title}" завершён! Рейтинг начислен {len(participants_with_places)} участникам.')
        return redirect('tournaments:tournament_list')

    return redirect('tournaments:tournament_edit', pk=pk)


def rating_list(request):
    """Список рейтинга игроков"""
    ratings = PlayerRating.objects.select_related('user').all()
    return render(request, 'tournaments/rating_list.html', {
        'ratings': ratings,
    })


@login_required
def adjust_rating(request, user_id):
    """Вычесть рейтинг у пользователя (только для staff)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав для изменения рейтинга')
        return redirect('tournaments:rating_list')

    target_user = get_object_or_404(User, pk=user_id)

    if target_user.is_staff:
        messages.error(request, 'Нельзя изменять рейтинг администратора')
        return redirect('tournaments:rating_list')

    if request.method == 'POST':
        action = request.POST.get('action')
        amount = request.POST.get('amount')

        try:
            amount = int(amount)
            if amount <= 0:
                messages.error(request, 'Сумма должна быть больше 0')
                return redirect('tournaments:rating_list')
        except (ValueError, TypeError):
            messages.error(request, 'Введите корректное число')
            return redirect('tournaments:rating_list')

        player_rating, created = PlayerRating.objects.get_or_create(
            user=target_user,
            defaults={'rating': 0}
        )

        if action == 'subtract':
            new_rating = player_rating.rating - amount
            if new_rating < 0:
                messages.warning(request, 'Рейтинг не может быть меньше 0. Установлено 0')
                player_rating.rating = 0
            else:
                player_rating.rating = new_rating
                messages.success(request, f'Вычтено {amount} баллов у {target_user.get_full_name() or target_user.username}')

        player_rating.save()

    return redirect('tournaments:rating_list')