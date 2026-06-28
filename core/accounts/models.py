from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    """Расширение стандартного пользователя Django"""
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        EMPLOYEE = 'EMPLOYEE', 'Сотрудник'
        MANAGER = 'MANAGER', 'Менеджер'

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField("Роль", max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    # avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"