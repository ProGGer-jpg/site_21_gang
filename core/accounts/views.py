from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, EmployeeRegistrationForm


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
    """Профиль текущего сотрудника"""
    profile = request.user.employeeprofile
    return render(request, 'accounts/profile.html', {'profile': profile})