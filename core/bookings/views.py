from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import QuickBookingForm
from .models import Booking
from catalog_21.models import Disc, Game, Room


@login_required
def quick_booking(request):
    # 1. Автоматически завершаем все истекшие брони
    Booking.objects.filter(
        status='ACTIVE',
        end_time__lt=timezone.now()
    ).update(status='COMPLETED')

    # 2. Получаем параметр disc из URL
    disc_id = request.GET.get('disc')
    room_id = request.GET.get('room')

    # 3. Обработка формы
    if request.method == 'POST':
        form = QuickBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'ACTIVE'
            booking.save()
            messages.success(request, f'✅ Успешно! {booking.client_name} забронировал {booking.disc.game.title}')
            return redirect('quick_booking')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = QuickBookingForm(user=request.user)
        # Если есть параметр disc в URL, устанавливаем его в форму
        if disc_id:
            form.set_disc_from_url(disc_id)
        if room_id:
            form.set_room_from_url(room_id)

    # 4. Разделяем брони
    now = timezone.now()
    active_bookings = Booking.objects.filter(
        status='ACTIVE', start_time__lte=now, end_time__gte=now
    ).order_by('end_time')[:10]

    planned_bookings = Booking.objects.filter(
        status='ACTIVE', start_time__gt=now
    ).order_by('start_time')[:10]

    return render(request, 'bookings/quick_booking.html', {
        'form': form,
        'active_bookings': active_bookings,
        'planned_bookings': planned_bookings,
        'now': now,
    })


@login_required
def games_catalog(request):
    """Каталог всех игр со статусами"""
    now = timezone.now()

    # Получаем все диски с информацией о том, заняты ли они сейчас
    discs = Disc.objects.select_related('game', 'game__platform').all()

    # Для каждого диска определяем статус
    discs_with_status = []
    for disc in discs:
        # Проверяем, есть ли активная бронь на этот диск прямо сейчас
        is_active = Booking.objects.filter(
            disc=disc,
            status='ACTIVE',
            start_time__lte=now,
            end_time__gte=now
        ).exists()

        discs_with_status.append({
            'disc': disc,
            'is_active': is_active,
        })

    return render(request, 'bookings/games_catalog.html', {
        'discs_with_status': discs_with_status,
    })


@login_required
def rooms_catalog(request):
    """Каталог всех комнат со статусами"""
    now = timezone.now()

    # Получаем все комнаты
    rooms = Room.objects.select_related('platform').filter(is_active=True)

    rooms_with_status = []
    for room in rooms:
        # Проверяем, занята ли комната прямо сейчас
        is_active = Booking.objects.filter(
            room=room,
            status='ACTIVE',
            start_time__lte=now,
            end_time__gte=now
        ).exists()

        rooms_with_status.append({
            'room': room,
            'is_active': is_active,
        })

    return render(request, 'bookings/rooms_catalog.html', {
        'rooms_with_status': rooms_with_status,
    })