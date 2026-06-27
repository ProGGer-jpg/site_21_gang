from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .forms import QuickBookingForm
from .models import Booking
from django.contrib.auth.decorators import login_required


@login_required
def quick_booking(request):
    # 1. Автоматически завершаем все истекшие брони
    Booking.objects.filter(
        status='ACTIVE',
        end_time__lt=timezone.now()
    ).update(status='COMPLETED')

    # 2. Обработка формы
    if request.method == 'POST':
        form = QuickBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'ACTIVE'
            booking.employee = request.user
            booking.save()
            messages.success(request, f'✅ Успешно! {booking.client_name} забронировал {booking.disc.game.title}')
            return redirect('quick_booking')
        else:
            # Показываем ошибки (например, диск занят)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        form = QuickBookingForm()

    # 3. Разделяем брони на две категории
    now = timezone.now()

    active_bookings = Booking.objects.filter(
        status='ACTIVE',
        start_time__lte=now,
        end_time__gte=now
    ).order_by('end_time')[:10]

    planned_bookings = Booking.objects.filter(
        status='ACTIVE',
        start_time__gt=now
    ).order_by('start_time')[:10]

    return render(request, 'bookings/quick_booking.html', {
        'form': form,
        'active_bookings': active_bookings,
        'planned_bookings': planned_bookings,
        'now': now,
    })