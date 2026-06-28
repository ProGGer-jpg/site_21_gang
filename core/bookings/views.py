from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import QuickBookingForm
from .models import Booking

@login_required
def quick_booking(request):
    # 1. Автоматически завершаем все истекшие брони
    Booking.objects.filter(
        status='ACTIVE',
        end_time__lt=timezone.now()
    ).update(status='COMPLETED')

    # 2. Обработка формы
    if request.method == 'POST':
        # Передаем пользователя в форму
        form = QuickBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'ACTIVE'
            booking.employee = request.user  # Автоматически указываем сотрудника
            booking.save()
            messages.success(request, f'✅ Успешно! {booking.client_name} забронировал {booking.disc.game.title}')
            return redirect('quick_booking')
        else:
            # Показываем ошибки
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"❌ {error}")
    else:
        # Передаем пользователя в форму при GET запросе
        form = QuickBookingForm(user=request.user)

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