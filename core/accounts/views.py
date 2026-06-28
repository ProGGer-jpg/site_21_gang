from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from bookings.models import Booking
from .forms import LoginForm, EmployeeRegistrationForm
from .models import EmployeeProfile


def login_view(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('quick_booking')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
                return redirect('quick_booking')
            else:
                messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('login')


@login_required
def register_employee(request):
    """Регистрация нового сотрудника (только для админов)"""
    if not request.user.is_staff:
        messages.error(request, 'Только администраторы могут регистрировать сотрудников')
        return redirect('quick_booking')

    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Сотрудник {user.get_full_name()} успешно зарегистрирован')
            return redirect('quick_booking')
    else:
        form = EmployeeRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """Профиль текущего сотрудника с его бронями"""
    profile, created = EmployeeProfile.objects.get_or_create(user=request.user)

    # Определяем, какие брони показывать
    if request.user.is_superuser:
        # Админ видит все активные брони
        user_bookings = Booking.objects.filter(status='ACTIVE').order_by('-start_time')
    else:
        # Обычный сотрудник видит только свои брони
        user_bookings = Booking.objects.filter(
            employee=request.user,
            status='ACTIVE'
        ).order_by('-start_time')

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'user_bookings': user_bookings,
        'now': timezone.now(),
    })


@login_required
def cancel_booking(request, booking_id):
    """Отмена брони"""
    booking = get_object_or_404(Booking, id=booking_id)

    # Проверяем права: можно отменить только свою бронь или если ты админ
    if booking.employee != request.user and not request.user.is_superuser:
        messages.error(request, '❌ У вас нет прав для отмены этой брони')
        return redirect('profile')

    # Проверяем, что бронь еще активна
    if booking.status != 'ACTIVE':
        messages.warning(request, '⚠️ Эта бронь уже не активна')
        return redirect('profile')

    # Отменяем бронь
    booking.status = 'CANCELED'
    booking.save()

    messages.success(request, f'✅ Бронь {booking.client_name} успешно отменена')
    return redirect('profile')