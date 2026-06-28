from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdminCommentForm, GameRequestForm
from .models import GameRequest


@login_required
def submit_request(request):
    """Подача новой заявки сотрудником."""
    if request.method == 'POST':
        form = GameRequestForm(request.POST)
        if form.is_valid():
            game_request = form.save(commit=False)
            game_request.requester = request.user
            game_request.save()
            messages.success(request, f'Заявка «{game_request.title}» успешно отправлена!')
            return redirect('game_requests:request_list')
    else:
        form = GameRequestForm()

    return render(request, 'game_requests/submit_request.html', {'form': form})


@login_required
def request_list(request):
    """Список заявок: админы видят все, сотрудники — только свои."""
    if request.user.is_staff:
        requests_qs = GameRequest.objects.select_related('platform', 'requester').all()
    else:
        requests_qs = GameRequest.objects.select_related('platform').filter(requester=request.user)

    status_filter = request.GET.get('status')
    if status_filter and status_filter in dict(GameRequest.STATUS_CHOICES):
        requests_qs = requests_qs.filter(status=status_filter)

    return render(request, 'game_requests/request_list.html', {
        'requests': requests_qs,
        'status_choices': GameRequest.STATUS_CHOICES,
        'current_status': status_filter,
    })


@login_required
def request_detail(request, pk):
    """Детали заявки + форма смены статуса для админов."""
    game_request = get_object_or_404(GameRequest, pk=pk)

    # Обычный сотрудник видит только свои заявки
    if not request.user.is_staff and game_request.requester != request.user:
        messages.error(request, 'У вас нет доступа к этой заявке.')
        return redirect('game_requests:request_list')

    admin_form = None
    if request.user.is_staff and request.method == 'POST':
        admin_form = AdminCommentForm(request.POST, instance=game_request)
        if admin_form.is_valid():
            admin_form.save()
            messages.success(request, 'Статус заявки обновлён.')
            return redirect('game_requests:request_detail', pk=pk)
    elif request.user.is_staff:
        admin_form = AdminCommentForm(instance=game_request)

    return render(request, 'game_requests/request_detail.html', {
        'game_request': game_request,
        'admin_form': admin_form,
    })