from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from catalog_21.models import Disc, Room
from django.contrib.auth.models import User
from datetime import timedelta


class Booking(models.Model):
    MAX_HOURS = 3
    """Запись в тетради (Бронирование)"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Активна'
        COMPLETED = 'COMPLETED', 'Завершена'
        CANCELED = 'CANCELED', 'Отменена'

    # Данные клиента (оставляем текстом для скорости, как в тетради)
    client_name = models.CharField("Имя клиента", max_length=100)
    client_phone = models.CharField("Телефон", max_length=20, blank=True)

    employee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Оформил сотрудник",
        null=True,
        blank=True
    )

    # Связь с каталогом
    disc = models.ForeignKey(Disc, on_delete=models.PROTECT, verbose_name="Диск с игрой")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name="Комната")

    # Время
    start_time = models.DateTimeField("Начало")
    end_time = models.DateTimeField("Конец")

    # Статус и доп. инфо
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField("Комментарий админа", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def clean(self):
        """Проверка на пересечение броней и ограничение по времени"""
        super().clean()
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time

            # 1. Проверка логики времени
            if self.start_time >= self.end_time:
                raise ValidationError("Время начала должно быть раньше времени конца.")

            # 2. Запрет бронирования в прошлом
            # Мы даем "окно" в 5 минут, чтобы можно было редактировать брони, которые только что начались
            if self.start_time < timezone.now() - timedelta(minutes=5):
                raise ValidationError("Нельзя создавать брони в прошлом.")

            # 3. Проверка на максимальное время (3 часа)
            if duration > timedelta(hours=self.MAX_HOURS):
                raise ValidationError(
                    f"Бронирование не может быть дольше {self.MAX_HOURS} часов."
                )

            # 4. Проверка на минимальное время (30 минут)
            if duration < timedelta(minutes=30):
                raise ValidationError("Минимальное время бронирования — 30 минут.")

            # 5. Проверка на пересечения (самая важная)
            overlapping = Booking.objects.filter(
                disc=self.disc,
                status='ACTIVE',
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(f"Диск '{self.disc}' уже забронирован на это время!")

    def __str__(self):
        return f"{self.client_name} -> {self.disc.game.title} ({self.start_time:%d.%m %H:%M})"

    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ['-start_time']